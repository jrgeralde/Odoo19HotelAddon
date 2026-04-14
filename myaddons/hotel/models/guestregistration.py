# -*- coding: utf-8 -*-

#guestregistration.py
import pytz
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class guestregistration(models.Model):

    _name = 'hotel.guestregistration'
    _description = 'hotel guest registration list'
    
    grc_id = fields.Integer(string="GRC #")
    room_id = fields.Many2one("hotel.rooms", string="Room No.")
    guest_id = fields.Many2one("hotel.guests", string="Guest Name")

    #roomname -< related fields found in the model hotel.rooms  
    roomname=fields.Char("Room Number", related='room_id.name') 

    #roomtname <- room type name found in the model hotel.rooms 
    # also related to hotel.roomtypes
    roomtname=fields.Char("Room Type",related='room_id.roomtypename')   

    # the model hotel.guests
    guestname=fields.Char("Guest Full Name", related='guest_id.name')
    guestemail=fields.Char("Guest Email", related='guest_id.email')

    creator_login = fields.Char(string="Created by", 
        related="create_uid.login",
        store=False, 
        readonly=True
    )

    datefromsched = fields.Datetime('Scheduled Check In', required=True, index=True, copy=False, default=fields.Datetime.now)
    datetosched = fields.Datetime('Scheduled Check Out', required=True, index=True, copy=False, default=fields.Datetime.now)

    #uncomment later for guest billing 
    roombill_ids=fields.One2many('hotel.roombill','guestregistration_id', string='Room Charges')          
     
      
    state = fields.Selection([
        ('DRAFT','Draft'),
        ('RESERVED','Reserved'),
        ('CHECKEDIN','Checked In'), 
        ('CHECKEDOUT','Checked Out'),                
        ('CANCELLED','Cancelled')],
        string="Status", default="DRAFT")

    actualpax = fields.Integer("Actual PAX")
    details=fields.Text("Details")  
  
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,  # auto-assign current user's company
    )

    def get_roombill_pages(self, page_size=65):
        """
        Returns a list of lists, each sublist contains up to page_size roombill lines.
        Usage: for page in record.get_roombill_pages(): ...
        """
        self.ensure_one()
        lines = self.roombill_ids
        return [lines[i:i+page_size] for i in range(0, len(lines), page_size)]

    total_amount_applied = fields.Float(
            string="Total Balance", 
            compute="_compute_total_amount_applied", 
            store=False, #True, Set store=True so it's searchable and performant
            digits=(12, 2)
        )
    @api.depends('roombill_ids.amountapplied', 'roombill_ids.state')
    def _compute_total_amount_applied(self):
        for rec in self:
        # Filter only FINAL bills
            bills = rec.roombill_ids.filtered(lambda b: b.state == 'FINAL')
            
            # Sum amountapplied, negating for document_id 3 or 5
            rec.total_amount_applied = sum(
                -b.amountapplied if b.document_id.id in (3, 5) else b.amountapplied
                for b in bills
            )

    total_amount_appliedstr = fields.Char(
            string="Total Balance", 
            compute="_compute_total_amount_appliedstr", 
            store=False  #True, Set store=True so it's searchable and performant
            
        )
    @api.depends('roombill_ids.amountapplied', 'roombill_ids.state')
    def _compute_total_amount_appliedstr(self):
        for rec in self:
            # Filter only FINAL bills
            bills = rec.roombill_ids.filtered(lambda b: b.state == 'FINAL')
            
            # Compute sum with document_id logic
            total = sum(
                -b.amountapplied if b.document_id.id in (3, 5) else b.amountapplied
                for b in bills
            )
            
            # Format as string with parentheses if negative
            if total < 0:
                rec.total_amount_appliedstr = f"({abs(total):,.2f})"
            else:
                rec.total_amount_appliedstr = f"{total:,.2f}"

    name= fields.Char("Guest Registration",compute='_compute_name',store=False)  
    @api.depends('room_id', 'guest_id')
    def _compute_name(self):
        for rec in self:
            rec.name= f"{rec.roomname}, {rec.guestname}"

    create_date_ampm = fields.Char(
       string="Created ON",
        compute='_compute_create_date_ampm',
        store=False  # not stored in the database
    )

    @api.depends('create_date')
    def _compute_create_date_ampm(self):
        user_tz = self.env.user.tz or 'UTC'
        for rec in self:
            if rec.create_date:
                # convert from UTC to user timezone
                dt_utc = fields.Datetime.from_string(rec.create_date)
                dt_local = pytz.utc.localize(dt_utc).astimezone(pytz.timezone(user_tz))
                # format with AM/PM
                rec.create_date_ampm = dt_local.strftime('%m-%d-%Y %I:%M %p')
            else:
                rec.create_date_ampm = ''


    datefromsched_ampm = fields.Char(
       string="Check In Date",
        compute='_compute_datefromsched_ampm',
        store=False  # not stored in the database
    )

    @api.depends('datefromsched')
    def _compute_datefromsched_ampm(self):
        user_tz = self.env.user.tz or 'UTC'
        for rec in self:
            if rec.datefromsched:
                # convert from UTC to user timezone
                dt_utc = fields.Datetime.from_string(rec.datefromsched)
                dt_local = pytz.utc.localize(dt_utc).astimezone(pytz.timezone(user_tz))
                # format with AM/PM
                rec.datefromsched_ampm = dt_local.strftime('%m-%d-%Y %I:%M %p')
            else:
                rec.datefromsched_ampm = ''

    datetosched_ampm = fields.Char(
       string="Check Out Date",
        compute='_compute_datetosched_ampm',
        store=False  # not stored in the database
    )

    @api.depends('datetosched')
    def _compute_datetosched_ampm(self):
        user_tz = self.env.user.tz or 'UTC'
        for rec in self:
            if rec.datetosched:
                # convert from UTC to user timezone
                dt_utc = fields.Datetime.from_string(rec.datetosched)
                dt_local = pytz.utc.localize(dt_utc).astimezone(pytz.timezone(user_tz))
                # format with AM/PM
                rec.datetosched_ampm = dt_local.strftime('%m-%d-%Y %I:%M %p')
            else:
                rec.datetosched_ampm = ''


    grc_id_display = fields.Char(
        string="GRC #",
        compute="_compute_grc_id_display",
        store=False
    )

    @api.depends('grc_id')
    def _compute_grc_id_display(self):
        for rec in self:
            rec.grc_id_display = str(rec.grc_id)

  # in guestregistration.py, append the following code:

    @api.model
    def create(self, vals_list):
    # vals_list can be a list of dicts
        for vals in vals_list:
            if not vals.get('grc_id'):
                doctype = 'GRC'
                cmp_id = self.env.company.id

                self.env.cr.execute("SELECT * FROM public.hotel_fnGetDocno(%s,%s)", (cmp_id,doctype))
        
                # Fetch the result
            
                result = self.env.cr.fetchone()
        
                vals['grc_id'] = result[0] if result else 1

        # Call the super with the list
        records = super().create(vals_list)
        return records     

    def action_reserve(self):
        self.ensure_one()

        if not(self.guest_id):  
            raise ValidationError('Please supply a valid guest.')            
        
        elif not(self.roomname):    
            raise ValidationError('Please supply a valid Room Number.')    
        elif not(self.datefromsched):    
            raise ValidationError('Please supply a valid Date From Schedule.')          
        elif not(self.datetosched):    
            raise ValidationError('Please supply a valid Date To Schedule.')          
        elif (self.datetosched<=self.datefromsched):    
            raise ValidationError('Invalid Date Range.')          
        elif fields.Datetime.now() > self.datefromsched:
            raise ValidationError('Cannot reserve past the scheduled check-in date.')
        elif fields.Datetime.now() >= self.datetosched:
            raise ValidationError('Cannot reserve past the scheduled check-out date.')
        else:

            # 2. Database Call
            pkid = self.id
            cmp_id = self.env.company.id

            # Using fetchone() is cleaner since the function returns a single row
            self.env.cr.execute("SELECT rid, rmessage FROM public.hotel_fncheck_registrationconflict(%s,%s)", (pkid, cmp_id))
            result = self.env.cr.fetchone() 
            if result and result[0] == 0:
                self.state = "RESERVED"
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Availability Check',
                        'message': 'The room is RESERVED for the selected dates.',
                        'type': 'success',
                        'sticky': False,
                        'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                    }
                }
            else:
                raise ValidationError(result[1] if result else "Schedule Conflict. Please check room availability for the selected dates.")    

    def action_checkin(self):
        for rec in self:
            if not(rec.guest_id):  
                raise ValidationError('Please supply a valid guest.')            
          
            elif not(rec.roomname):    
                raise ValidationError('Please supply a valid Room Number.')    
            elif not(rec.datefromsched):    
                raise ValidationError('Please supply a valid Date From Schedule.')          
            elif not(rec.datetosched):    
                raise ValidationError('Please supply a valid Date To Schedule.')          
            elif (rec.datetosched<=rec.datefromsched):    
                raise ValidationError('Invalid Date Range.')          
            elif fields.Datetime.now() < rec.datefromsched:
                raise ValidationError('Cannot check in before the scheduled check-in date.')
            elif fields.Datetime.now() >= rec.datetosched:
                raise ValidationError('Cannot check in past the scheduled check-out date.')
            else:
    
                # 2. Database Call
                pkid = self.id
                cmp_id = self.env.company.id

                # Using fetchone() is cleaner since the function returns a single row
                self.env.cr.execute("SELECT rid, rmessage FROM public.hotel_fncheck_registrationconflict(%s,%s)", (pkid, cmp_id))
                result = self.env.cr.fetchone() 

                if result and result[0] == 0:
                    now = fields.Datetime.now()
                    if rec.datefromsched != now:
                        rec.datefromsched = now
                    
                    self.env.cr.execute("SELECT * FROM public.hotel_fnCheckin(%s,%s)", (pkid,cmp_id,))
                    rec.state = "CHECKEDIN"
               
                    self.env.cr.fetchall()

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Check In',
                            'message': 'Guest has been CHECKED IN successfully.',
                            'type': 'success',
                            'sticky': False,
                            'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                        }
                    }

                else:
                    raise ValidationError(result[1] if result else "Schedule Conflict. Please check room availability for the selected dates.")    
               

    def action_checkout(self):
        for rec in self:
            if (rec.state=="CHECKEDIN"):  
                rec.state= "CHECKEDOUT"
            else:                     
                raise ValidationError("Guest is not CHECKED IN.") 


    def action_cancel(self):
        for rec in self:
            if (rec.state=="CHECKEDIN"):  
                raise ValidationError("Guest has already CHECKED IN.")           
            else:                     
                rec.state= "CANCELLED"

    #---------------Check Availability Button Action-----------------
    
    def action_mark_draft(self):
        for rec in self:
            rec.state = "DRAFT"       

    #def action_refresh_guest_list(self):

        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'hotel.guestregistration',
        #     'view_mode': 'list,form',
        #     'target': 'current',
        #     'domain': self.env.context.get('domain', []),
        #     'context': self.env.context,
        # }

    def action_refresh_guest_list(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
   
        }
    

    def action_check_availability(self):

        self.ensure_one()  # self is now your 'rec'

        # 1. Validation Checks
        if not self.guest_id:  
            raise ValidationError(_('Please supply a valid guest.'))            
        if not self.room_id: # Usually room_id in Odoo, check your field name   
            raise ValidationError(('Please supply a valid Room Number.'))    
        if not self.datefromsched:    
            raise ValidationError(('Please supply a valid Date From Schedule.'))          
        if not self.datetosched:    
            raise ValidationError(('Please supply a valid Date To Schedule.'))          
        if self.datetosched <= self.datefromsched:    
            raise ValidationError(('Invalid Date Range: Check-out must be after Check-in.'))          

        # 2. Database Call
        pkid = self.id
        cmp_id = self.env.company.id

        # Using fetchone() is cleaner since the function returns a single row
        self.env.cr.execute("SELECT rid, rmessage FROM public.hotel_fncheck_registrationconflict(%s,%s)", (pkid, cmp_id))
        result = self.env.cr.fetchone() 

        if result:
            result_cnt = result[0]
            result_msg = result[1]

            if result_cnt == 0:
                # For a Button Action, use display_notification for the "Success" message
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ("Availability Check"),
                        'message': ("The room schedule is available for the selected dates."),
                        'type': 'success',
                        'sticky': False,
                    }
                }   
                
            else:
                # Use ValidationError for the "Conflict" to block the user
                raise ValidationError(result_msg)
        
        return True
    
    def action_check_availability(self):
        self.ensure_one()  # self is now your 'rec'

        # 1. Validation Checks
        if not self.guest_id:  
            raise ValidationError(_('Please supply a valid guest.'))            
        if not self.room_id: # Usually room_id in Odoo, check your field name   
            raise ValidationError(_('Please supply a valid Room Number.'))    
        if not self.datefromsched:    
            raise ValidationError(_('Please supply a valid Date From Schedule.'))          
        if not self.datetosched:    
            raise ValidationError(_('Please supply a valid Date To Schedule.'))          
        if self.datetosched <= self.datefromsched:    
            raise ValidationError(_('Invalid Date Range: Check-out must be after Check-in.'))          

        # 2. Database Call
        pkid = self.id
        cmp_id = self.env.company.id

        # Using fetchone() is cleaner since the function returns a single row
        self.env.cr.execute("SELECT rid, rmessage FROM public.hotel_fncheck_registrationconflict(%s,%s)", (pkid, cmp_id))
        result = self.env.cr.fetchone() 

        if result:
            result_cnt = result[0]
            result_msg = result[1]

            if result_cnt == 0:
                # For a Button Action, use display_notification for the "Success" message
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ("Availability Check"),
                        'message': ("The room schedule is available for the selected dates."),
                        'type': 'success',
                        'sticky': False,
                    }
                }   
                
            else:
                # Use ValidationError for the "Conflict" to block the user
                raise ValidationError(result_msg)
        
        return True

