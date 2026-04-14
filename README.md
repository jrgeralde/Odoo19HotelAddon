# Odoo 19 Hotel Addon Installation Guide

1. Requirements:
     Ubuntu 22
     Python 3.12
     Postgresql 18 and PGadmin4
     VS Code

2.  Install Odoo 19 using the First Playlist (16 Videos) : https://www.youtube.com/playlist?list=PLSXU7mHsq8yntYp8dBb7rM-fmgFlbaksW

3.  Download the following github repository and copy the whole myaddons folder under your project folder:

     https://github.com/jrgeralde/Odoo19HotelAddon

4.  Update your odoo.conf to include the myaddons folder, Example:
     
      ; Addon paths (relative)
     ; addons_path = addons,odoo/addons,mukwebthemeaddon,myaddons

5.  Install the hotel Application and exit.

6.   Open your postgresql database in PGADMIN and Using the storedprocs folder, run the following scripts (in sequence) using the PGADMIN query tool.

               Inserthoteldocuments.sql
               createindexforRegistrationconflict.sql
               hotel_fngetdocno.sql
               hotel_fnapplyguestcurrentroomcharge.sql
               hotel_fncheckin.sql
               hotel_fnCheck_RegistrationConflict.sql
               create_hotel_transaction_report_view.sql

7.  Run the Hotel Application and add sample records for:

           charges (ROOM CHARGE, CASH,VISA, MEALS, LAUNDRY, PATRONAGE DISCOUNT, PWD DISCOUNT)
           roomtypes (with daily charges) (SINGLE, DOUBLE, TWIN, MATRIMONIAL)
           rooms
           guests

8.  Test  the Hotel registration (create, reserve, checkin, checkout cancel)

9.  Test adding of charges and payments for check in guests

10.  Test the reports, guest bills and email sending.





