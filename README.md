# SW455-Project
Meeting Scheduling System (MSS)

Objectives
The purpose of this project is to develop a complete application using object-oriented paradigm.  This involves all development phases from requirements specification to implementation and testing. Throughout the development process quality and especially security should be considered. The techniques learned in course, to engineer quality and security in software, will be applied throughout this project. The application should be developed and documented using Software Engineering standards and UML.

Background
You are asked to engineer an application for a company called PennStateSoft. PennStateSoft is a game development company located in Pennsylvania and is currently employing over 100 people.  All employing are working in the company’s main office in Pittsburgh, PA.

Project Description
PennStateSoft is looking to create a meeting scheduling system (MSS). This MSS keeps track of meetings schedule and which people are in what meeting in which room. The application is not required to perform scheduling, rather it is responsible for maintaining the schedule. For simplicity, assume your application is maintaining the schedule for only one week and a meeting can only fall in traditional 9-5 business hours. Following are general guidelines:

1.	Each room has a number. A room should keep track of all meetings held in it.
2.	Each meeting has a name, time and room. A meeting should keep track of all people attending the meeting.
3.	A person cannot be attending more than one meeting in any one-hour slot.
4.	A room cannot hold more than one meeting at any one-hour slot.
5.	Rooms can be special or regular. To reserve a special room, a payment of $100 is required.
6.	Only meeting creators can add people to them.
7.	A person can only view the meetings they are participating in.

The system will enable two types of users, clients, and administrators. A client can:

•	Create an account using their unique company email address.
•	Check and update their profile information including payment information.
•	Create a meeting and reserve a room for it.
•	Pay for special rooms.
•	Add people to a meeting.
•	Remove people form a meeting.
•	Display and edit all the meetings they have created.
•	Display all the meetings they are going to participate in.
•	File a complaint.

The application will also have an administrative function where the administrator can:

•	Add or delete rooms available for meetings.
•	Update the clients’ billing information.
•	Few complaints and respond to them.
•	Display all meetings in a week, or a day.
•	Display all meetings in a specific room.
•	Display all the meetings attended by a single person.
•	Display all the meetings at a specific time slot.
•	Create other administrator accounts.

The client wants the system to be a web-based system, user-friendly and contains the company’s logo. Administrators will only need 2 hours of training to be able to use the system. Users should be able to use the system without training. Hints and help information should also be provided to clients and administrators when necessary.

Ideally, all the data would be stored in a database that can be easily accessed by the application administrator and reports can be generated.
