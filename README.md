This is one of my projects that I've done when I was still working with Oracle.

This notification system (with the 'notification.py' as the main program), is automatically sending 
a notification/alert message to user once an error (defined in 'errorfile.yml') has been encountered.
It uses the pdpyras python module as well as the existing 'EventsAPISession' API of Pagerduty to trigger 
a pagerduty notification.

A notification file 'notification.yml' is used to identify the group to be notified 
(based on the 'notification_file.yml') as well the notification type (either via pagerduty or ocean).
But please take note that the completed implementation done is limited only for Pagerduty, 
due to limited development time during the time of implementation, and also due to the fact that Ocean
system is still not yet been rolled out for use during the time this notification system has been 
developed.

To know how to run the notification system, kindly see the 'Notification tool sample output.PNG' file.
This has the screenshot on how to execute the application as well as the expected output.

There's also a sample screenshot file 'slack received alerts from pagerduty.PNG' 
that shows expected notification received by slack via pagerduty.
