#!/usr/bin/env python3
"""Obsidian-to-Jekyll publishing pipeline. Runs inside GitHub Actions."""

import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import frontmatter
import anthropic
import yaml
from slugify import slugify as _slugify


REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=REPO_ROOT, **kwargs)


def slugify_title(title):
    return _slugify(title, separator="-", lowercase=True)


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

def find_draft_file():
    """Return path to the .md file added/modified in drafts/ by this push."""
    result = _run(["git", "diff", "--name-only", "HEAD~1", "HEAD"])
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line.startswith("drafts/") and line.endswith(".md"):
            return REPO_ROOT / line
    return None


def load_draft(path):
    """Parse frontmatter and body. Returns (metadata dict, content str)."""
    post = frontmatter.load(str(path))
    return dict(post.metadata), post.content


# ---------------------------------------------------------------------------
# Obsidian syntax conversion
# ---------------------------------------------------------------------------

def convert_obsidian(content):
    """Convert Obsidian-specific markup to standard markdown."""
    # [[link|display]] -> display
    content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', content)
    # [[link]] -> link
    content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
    # ![[image.ext]] -> sentinel comment (images handled separately)
    content = re.sub(r'!\[\[([^\]]+)\]\]', r'<!-- obsidian-embed: \1 -->', content)
    # Strip inline #tags that appear after whitespace (not headings, not code)
    content = re.sub(r'(?<=\s)#([A-Za-z][A-Za-z0-9_-]*)\b', '', content)
    return content


# ---------------------------------------------------------------------------
# Image handling
# ---------------------------------------------------------------------------

def check_images(content, slug, draft_dir):
    """
    Detect image refs, copy found files to assets/images/<slug>/, rewrite paths.
    Returns (updated_content, moved_list, missing_list).
    """
    assets_dir = REPO_ROOT / "assets" / "images" / slug
    moved, missing = [], []

    # Collect referenced filenames
    refs = set()
    for m in re.finditer(r'<!-- obsidian-embed: ([^\s>]+) -->', content):
        refs.add(m.group(1))
    for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', content):
        src = m.group(1)
        if not src.startswith(("/", "http")):
            refs.add(os.path.basename(src.lstrip("./")))

    if not refs:
        return content, [], []

    assets_dir.mkdir(parents=True, exist_ok=True)
    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

    for filename in refs:
        found = None
        for f in draft_dir.rglob("*"):
            if f.name.lower() == filename.lower() and f.suffix.lower() in IMAGE_EXTS:
                found = f
                break

        if found:
            shutil.copy2(found, assets_dir / filename)
            moved.append(filename)
            new_path = "{{site.baseurl}}" + f"/assets/images/{slug}/{filename}"
            # Replace obsidian embed sentinel
            content = re.sub(
                rf'<!-- obsidian-embed: {re.escape(filename)} -->',
                f'![{filename}]({new_path})',
                content,
            )
            # Replace bare/relative markdown refs
            content = re.sub(
                rf'!\[([^\]]*)\]\(\.?/?{re.escape(filename)}\)',
                f'![\\1]({new_path})',
                content,
            )
        else:
            missing.append(filename)

    return content, moved, missing


# ---------------------------------------------------------------------------
# AI steps
# ---------------------------------------------------------------------------

def proof(content, client):
    """Return markdown-formatted proofreading suggestions."""
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": (
                "You are a copy editor reviewing a blog post draft. Identify issues with "
                "grammar, spelling, sentence structure, clarity, and coherence. For each issue: "
                "quote the problematic phrase (max 8 words), name the problem, give a specific "
                "correction. Output a numbered markdown list. Maximum 15 suggestions. "
                "Do NOT rewrite whole sections — one targeted suggestion per issue.\n\n"
                f"Post:\n{content}"
            ),
        }],
    )
    return resp.content[0].text


def generate_image(content, title, slug, client):
    """
    Generate a cover image via Gemini Imagen.
    Returns (jekyll_image_path, prompt_used).
    Falls back to placeholder if GEMINI_API_KEY is absent.
    """
    # Stage 1: Claude writes the image prompt
    prompt_resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": (
                "Write a concise image generation prompt (max 80 words) for a professional "
                "blog cover photo based on this post. Style: clean, modern, flat illustration "
                "or abstract graphic. No text or words in the image. Visually relevant to the "
                "topic. Output the prompt only, nothing else.\n\n"
                f"Title: {title}\n\nContent (excerpt):\n{content[:2000]}"
            ),
        }],
    )
    image_prompt = prompt_resp.content[0].text.strip()

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print(f"GEMINI_API_KEY not set — skipping image generation.\nPrompt: {image_prompt}", file=sys.stderr)
        return "/assets/images/placeholder.jpg", image_prompt

    import google.generativeai as genai

    genai.configure(api_key=gemini_key)
    model = genai.ImageGenerationModel("imagen-3.0-generate-002")
    result = model.generate_images(
        prompt=image_prompt,
        number_of_images=1,
        aspect_ratio="16:9",
    )

    dest = REPO_ROOT / "assets" / "images" / f"{slug}-cover.png"
    image_obj = result.images[0]

    # Save using whichever attribute is available in the installed SDK version
    if hasattr(image_obj, "_pil_image"):
        image_obj._pil_image.save(str(dest))
    elif hasattr(image_obj, "image_data"):
        from PIL import Image
        Image.open(io.BytesIO(image_obj.image_data)).save(str(dest))
    else:
        raise RuntimeError("Cannot extract image from Gemini response — check SDK version.")

    return f"/assets/images/{slug}-cover.png", image_prompt


def draft_linkedin(content, title, slug, client):
    """Return LinkedIn post text."""
    url = f"https://tomrook.co.uk/{slug}"
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": (
                "Write a LinkedIn post promoting this blog article. Requirements:\n"
                "- Hook opening line that grabs attention\n"
                "- 2-3 sentence summary of the key insight\n"
                "- Call to action with the article URL\n"
                "- 3-5 relevant hashtags\n"
                "- Under 300 words\n"
                "- Conversational, not corporate\n\n"
                f"Article title: {title}\n"
                f"Article URL: {url}\n\n"
                f"Article content:\n{content[:3000]}"
            ),
        }],
    )
    return resp.content[0].text


def build_frontmatter_fields(content, title, publish_date, image_path, client):
    """Ask Claude for categories/tags/description, return assembled frontmatter dict."""
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": (
                "Based on this blog post return JSON with exactly these fields:\n"
                '- "categories": array of 2-4 relevant categories (e.g. ["Salesforce", "Automation"])\n'
                '- "tags": array of 3-6 relevant tags\n'
                '- "description": one sentence, max 160 chars, suitable as a meta description\n\n'
                "Output valid JSON only — no markdown fences, no explanation.\n\n"
                f"Title: {title}\nContent:\n{content[:3000]}"
            ),
        }],
    )

    raw = resp.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    data = json.loads(raw)

    return {
        "layout": "post",
        "title": title,
        "date": publish_date,
        "author": "tom",
        "author_profile": "/about/",
        "categories": data.get("categories", []),
        "tags": data.get("tags", []),
        "image": image_path,
        "description": data.get("description", ""),
    }


# ---------------------------------------------------------------------------
# Frontmatter serialisation
# ---------------------------------------------------------------------------

class _InlineList(list):
    pass


def _inline_list_representer(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


yaml.add_representer(_InlineList, _inline_list_representer)


def serialise_frontmatter(fm):
    """Render frontmatter dict to YAML string, with inline arrays for categories/tags."""
    ordered = dict(fm)
    for key in ("categories", "tags"):
        if key in ordered:
            ordered[key] = _InlineList(ordered[key])
    return yaml.dump(ordered, default_flow_style=False, allow_unicode=True, sort_keys=False)


# ---------------------------------------------------------------------------
# Git + PR
# ---------------------------------------------------------------------------

def commit_and_pr(branch, post_filename, draft_path, title, proof_comment, linkedin_comment):
    gh_token = os.environ.get("GH_TOKEN", "")
    env = {**os.environ, "GH_TOKEN": gh_token}

    _run(["git", "config", "user.email", "actions@github.com"])
    _run(["git", "config", "user.name", "GitHub Actions"])
    _run(["git", "checkout", "-b", branch])

    # Stage new/changed files
    _run(["git", "add", "assets/images/", "_posts/"])

    # Remove the draft (and any sibling image files in drafts/)
    draft_dir = REPO_ROOT / "drafts"
    for f in draft_dir.iterdir():
        if f.name != ".gitkeep":
            _run(["git", "rm", "-f", str(f.relative_to(REPO_ROOT))])

    _run(["git", "commit", "-m", f"Publish: {title}"])

    # Push with retries
    for attempt, wait in enumerate([0, 2, 4, 8, 16]):
        if wait:
            import time
            time.sleep(wait)
        push = subprocess.run(
            ["git", "push", "-u", "origin", branch],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if push.returncode == 0:
            break
        if attempt == 4:
            print(f"Push failed after retries:\n{push.stderr}", file=sys.stderr)
            sys.exit(1)

    # Create PR
    pr = subprocess.run(
        ["gh", "pr", "create",
         "--title", f"Publish: {title}",
         "--body", (
             "Auto-generated by the Obsidian publishing pipeline.\n\n"
             "Review the suggestions in the comments below, then **merge to publish**."
         ),
         "--base", "main",
         "--head", branch],
        capture_output=True, text=True, cwd=REPO_ROOT, env=env,
    )
    if pr.returncode != 0:
        print(f"PR creation failed:\n{pr.stderr}", file=sys.stderr)
        sys.exit(1)

    pr_url = pr.stdout.strip()
    pr_number = pr_url.rstrip("/").split("/")[-1]
    print(f"PR created: {pr_url}")

    for body in [proof_comment, linkedin_comment]:
        subprocess.run(
            ["gh", "pr", "comment", pr_number, "--body", body],
            check=True, cwd=REPO_ROOT, env=env,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    draft_path = find_draft_file()
    if not draft_path:
        print("No draft .md found in this push — nothing to do.")
        sys.exit(0)

    print(f"📄 Processing: {draft_path.name}")

    metadata, content = load_draft(draft_path)
    content = convert_obsidian(content)

    title = (metadata.get("title") or
             draft_path.stem.replace("-", " ").replace("_", " "))
    slug = slugify_title(title)

    raw_date = metadata.get("date") or metadata.get("publish_date")
    publish_date = str(raw_date)[:10] if raw_date else str(date.today())

    # Images
    draft_dir = REPO_ROOT / "drafts"
    content, moved_images, missing_images = check_images(content, slug, draft_dir)

    image_report = ""
    if moved_images or missing_images:
        image_report = f"\n\n### 🖼 Images\n"
        if moved_images:
            image_report += f"✅ Moved to `assets/images/{slug}/`: {', '.join(moved_images)}\n"
        if missing_images:
            image_report += (
                f"⚠️ Missing — upload to `drafts/` and re-push: {', '.join(missing_images)}\n"
            )

    # Claude client
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    client = anthropic.Anthropic(api_key=anthropic_key)

    print("✏️  Proofreading...")
    proof_suggestions = proof(content, client)
    proof_comment = f"## ✏️ Proofreading Suggestions\n\n{proof_suggestions}{image_report}"

    print("🎨 Generating cover image...")
    image_path, image_prompt = generate_image(content, title, slug, client)

    print("💼 Drafting LinkedIn post...")
    linkedin_text = draft_linkedin(content, title, slug, client)
    substack_url = f"https://tomrook.co.uk/{slug}"
    linkedin_comment = (
        f"## 💼 LinkedIn Draft\n\n{linkedin_text}\n\n"
        f"---\n\n"
        f"### 📨 Substack Import\n"
        f"Once merged, import your post at:\n"
        f"`{substack_url}`\n\n"
        f"In Substack: **New Post → ··· → Import** → paste URL above"
    )

    print("📋 Building frontmatter...")
    fm = build_frontmatter_fields(content, title, publish_date, image_path, client)

    # Write post file
    post_filename = f"{publish_date}-{slug}.md"
    posts_dir = REPO_ROOT / "_posts"
    posts_dir.mkdir(exist_ok=True)

    fm_yaml = serialise_frontmatter(fm)
    final_content = f"---\n{fm_yaml}---\n\n{content.lstrip()}"
    (posts_dir / post_filename).write_text(final_content, encoding="utf-8")
    print(f"✅ Written: _posts/{post_filename}")

    # Commit and PR
    branch = f"publish/{publish_date}-{slug}"
    commit_and_pr(branch, post_filename, draft_path, title, proof_comment, linkedin_comment)


if __name__ == "__main__":
    main()
