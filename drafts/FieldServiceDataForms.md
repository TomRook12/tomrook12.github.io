---
Title: An idiots guide to Field Service Data Forms
status: Draft
tags:
  - Salesforce
  - FSL
  - Product Management
---

# An idiots guide to Salesforce Field Service Data Forms

This is the guide I wish I found when I was trying to configure these frankly fantastic little flows last month. If you haven't come across this particular type of flow it’s called a Data Capture flow and is specifically available with Salesforce Field Service, used on the Field Service mobile app. 

So if you happen to have field service and want a slick UI for your field service workers to capture data in the field then jump into this guide! The UI is great but getting there can be a struggle, I won’t cover actually making a flow, I’ll leave that up to you. Instead we’ll look into getting these things up and running.


> [!Note] The key concept
> Capture information and make DML statements and some basic actions from the field service mobile device. Fully offline utilising a specific type of screen flow and a special junction object that connects those screen flows to records of Work Orders, Service Appointments, Assets and Custom Objects.


### Setting up the org

This knocked me for 6. Unfortunately, Salesforce's help confused me more than anything else. So I spent ages trawling through my org toggling settings in vain. Many, many YouTube videos were consumed. Instead of that nonsense Follow these checks before building your first flow.

1. Enable access to Lightning SDK for Field Service Mobile:  
	- **Globally:** Field Service Settings > Enable Lightning SDK for Field Service Mobile. Every user everywhere gets this.
	- **Per User:** New Permission Set, System Permissions > Enable Lightning SDK for Field Service Mobile. (Make sure you assign it to your mobile workers!)  
2. Decide on Sharing for the junction object.
   - **Sharing Rules** -  Usual Salesforce sharing setup - Sharing Settings and create sharing rules for the Form object  (API Name DynamicDataCapture)
   - **Field Service Setup** - Enable the forms to be controlled by parent (access to the parent gives access the form) Setup > Field Service Settings >  Enable for ms to be c
1. **Forms on the desktop** Now you will need to add the related list (Forms) to the page layout(s) that you would like the forms to be linked to. 
2. **Forms in the App** - For it to appear in the app either wait (I am not that patient) or sign out and sign back in again. No amount of refreshing or clearing the cache worked for me. *(This was just in my sandbox, users in Production didn't need to do this step)*
3. **Usual Field Service Setup** - Also don't forget usual Field Service gubbins apply, the user trying to access the mobile app must have an active, Technician, Service Resource. Right skills, right territory to actually receive the work order/service appointment and will need a field service mobile licence. 
4. **Object permissions** Some standard profiles like System Admin and Standard User get access to this object by default everyone is else will need Create and Edit permissions to the object as well as
5. **Idiot check** Final, final, one here make sure the users have run flows as well.

*Nb: These flows do not run at all on desktop, apart from in flow debugging mode where some of their features don't work.*

### Setting up the flow

Like I mentioned, to start with these flows create just like normal screen flows, I won’t cover creating a screen flow as that has been done to death instead what we will look at is the main differences, gotchas and tricks.

First of all make sure you select the correct type of flow, it has be **Data Capture** only those work with the form junction object.

Once you create your flow it comes with 3 poorly labeled variables ready to go
**RecordId** - The id of the Form junction record. **Don't** populate this, it does not work like a normal 
**ParentRecordId** - The id of the record that this flow was started from e.g. the Work Order record’s ID  
**ParentObjectType** - The object type of the record that started this flow, eg Work order etc.

In no particular order here are some of the quirks:  
**DML** - Creates, Updates and Deletes must come at the end of the flow  
**Choice Resources** - Choice’s must have text outputs  
**Debug** - Debug functionality can be super weird with some elements like signature only running on the mobile device.
**Text Template** - There is no text template resource so if you are capturing a lot of text it can be hard to format.  
**Subflows -** Can only be other data capture flows and can’t perform DML  
**Actions** - There a limitations here eg. no post to chatter

[More Caveats can be found here](https://help.salesforce.com/s/articleView?id=service.mfs_data_capture_limitations.htm&type=5)

### Setting up the form

Settings configured, flow created and now time for your users to run it! If you haven't heard about this, basically for a user to see your beautiful data capture flow in their field service app you have to connect the Work Order/Service Appointment/Asset/Custom Object to your flow using the Form Junction object. It works as below:  
![][image1]

For the users to be able to see the flow a junction object must be created this can be done manually from the related record. This would obviously grow tedious so I would recommend creating a flow to make the junction object where required. Creating the records couldn't be simpler, add the triggering a records Id in Parent record and then add the API name of the flow into the Action Definition field. A record triggered flow based on work order type, territory, team etc. Works perfectly here.
