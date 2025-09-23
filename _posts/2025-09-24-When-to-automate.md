---
layout: post
title: "Deciding When to Automate"
date: 2025-09-23
author: tom
author_profile: /about/
categories: [technology, Salesforce, Automation]
image: /assets/images/FlowAutomate.png
tags: [technology, Salesforce, Automation]
---

When should a process be automated, what sort of process is a good candidate for automation? Is this a step by step guide or just me whining about people automating processes that they shouldn't and that aren’t understood yet? A mix of the two is what this probably is.

Shouldn’t I love automation? Isn’t automation what I do for a living? Well yes and no, I like to think what I do is work with  business processes. And business processes don’t have to be automated at all, in fact less automation gives more room for the process to scale as the business grows. Automating a process often leaves it brittle and unable to flex, bringing a process into automation requires constant support and maintenance. So when should a process be automated? 

Before we create fields, make a flow or write any apex we need to understand the process end-end. Understanding the process end-end means you know not only the touch points that will be within your system (as-is or to-be) but also what users are doing in other systems, when I say systems I don’t only mean things like Salesforce I mean outlook, the venerable excel and anything that is occurring side of desk - are users running this from a whiteboard in the office? How can we lock something into such a rigid process if we don’t understand it? If we don’t know who is involved? 
## So when should be automate? 
Working through a process end-end can be challenging so what about some quick wins? In my opinion there are always two clear candidates, that we should look too first:

**Mature Processes** - Anything that has been a long standing part of the fabric of the business - this can be a great opportunity as often this type of process is ripe for innovation. Probably also something that gives users a massive headache, so could provide quick time to value!

**Compliance (inc. legal & finance) Processes** - Anything that users MUST do, certain information required by external bodies, governance or contractual items. What can be challenging here is wading through the litres of nonsense and identifying what is actually important. 

Of course you could automate anything but the above, is a good starting point that will add value quickly.
## So you wanna automate?
You have identified a process that you want to automate (great job!) Now we want to bring that process into Salesforce, but can we do it in a way that lets the process grow and develop and gives us a way to start capturing user feedback? I would advocate for MVP, a whole series of blog posts could probably be written on MVP. Minimum Viable Product or MVP is the simplest version of something that still gets the users into the platform and doing their role. This reduces risk (we haven’t spent ages building something massive, we can easily pivot to something different), we can validate what we have made and iterate (I love to iterate). 

So to clarify this half ramble-half instructional adventure:
1. Know the consequences of over engineering your automation
2. Understand what you are automating
3. Do the absolute minimum (MVP)
4. Gather feedback and iterate!
