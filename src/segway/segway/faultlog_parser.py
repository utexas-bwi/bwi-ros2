"""--------------------------------------------------------------------
COPYRIGHT 2014 Stanley Innovation Inc.

Software License Agreement:

The software supplied herewith by Stanley Innovation Inc. (the "Company") 
for its licensed Segway RMP Robotic Platforms is intended and supplied to you, 
the Company's customer, for use solely and exclusively with Stanley Innovation 
products. The software is owned by the Company and/or its supplier, and is 
protected under applicable copyright laws.  All rights are reserved. Any use in 
violation of the foregoing restrictions may subject the user to criminal 
sanctions under applicable laws, as well as to civil liability for the 
breach of the terms and conditions of this license. The Company may 
immediately terminate this Agreement upon your use of the software with 
any products that are not Stanley Innovation products.

The software was written using Python programming language.  Your use 
of the software is therefore subject to the terms and conditions of the 
OSI- approved open source license viewable at http://www.python.org/.  
You are solely responsible for ensuring your compliance with the Python 
open source license.

You shall indemnify, defend and hold the Company harmless from any claims, 
demands, liabilities or expenses, including reasonable attorneys fees, incurred 
by the Company as a result of any claim or proceeding against the Company 
arising out of or based upon: 

(i) The combination, operation or use of the software by you with any hardware, 
    products, programs or data not supplied or approved in writing by the Company, 
    if such claim or proceeding would have been avoided but for such combination, 
    operation or use.
 
(ii) The modification of the software by or on behalf of you 

(iii) Your use of the software.

 THIS SOFTWARE IS PROVIDED IN AN "AS IS" CONDITION. NO WARRANTIES,
 WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT NOT LIMITED
 TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 PARTICULAR PURPOSE APPLY TO THIS SOFTWARE. THE COMPANY SHALL NOT,
 IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL OR
 CONSEQUENTIAL DAMAGES, FOR ANY REASON WHATSOEVER.
 
 \file   faultlog_parser.py

 \brief  This module contains a class for parsing the faultlog into
         human readable form

 \Platform: Linux/ROS Indigo
--------------------------------------------------------------------"""
from .system_defines import *
from .utils          import *
from .crc16 import buffer_crc_is_valid
import math
import webbrowser
import os
import time
import array


"""
Class for faultlog extraction
"""
class FaultlogParser:
    def __init__(self,faultlog_array):
               
        """
        If this path does not exists make it it is the default path for the
        faultlog extraction
        """
        if (False == os.path.exists(os.getcwd()+"/RMP_CCU_FAULTLOGS")):
            os.mkdir(os.getcwd()+"/RMP_CCU_FAULTLOGS")
        
        """
        Get the directory and make sure the user did not cancel
        """
        self.dir_path = os.getcwd()+ "/RMP_CCU_FAULTLOGS"
        
        """
        Parse the faultlog array
        """
        filename = self.dir_path + "/" + "RMP_CCU_FAULTOG_" + time.strftime("%m%d%Y_%H%M%S") + ".html"     
        Create_Log_File(filename,faultlog_array.data)
        try:
            webbrowser.open(filename)
        except:
            webbrowser.open(filename)        

"""
Begin faultlog file creation functions and variables
"""
MAX_FAULT_ENTRIES = 20;
NUMBER_OF_ITEMS_PER_ENTRY = 15;
NUMBER_OF_FAULT_GROUPS = 8;

fault_group_names = ["Transient Faults",
                     "Critical Faults",
                     "Communication Faults",
                     "Sensor Faults",
                     "BSA Faults",
                     "Motordrive Faults",
                     "Architecture Faults",  
                     "Internal Faults"];
                     
decode_list = [transient_fault_decode,
               critical_fault_decode,
               comm_fault_decode,
               sensor_fault_decode,
               bsa_fault_decode,
               mcu_fault_decode,
               arch_fault_decode,
               internal_fault_decode]

"""
Define calender constants
"""
NUMBER_OF_MONTHS_PER_YEAR  = (12)
SECONDS_PER_MINUTE         = (60)
SECONDS_PER_HOUR           = (3600)
SECONDS_PER_DAY            = (86400)
SECONDS_PER_YEAR           = (31536000)
SECONDS_PER_LEAP_YEAR      = (31622400)

days_per_month = [31, #January
                  28, #February (in non-leap years)
                  31, #March
                  30, #April
                  31, #May
                  30, #June
                  31, #July
                  31, #August
                  30, #September
                  31, #October
                  30, #November
                  31  #December
                  ];
    
"""
Convert the seconds in the fault log to an actual date based on the
origin date
"""
def seconds_to_date(seconds):
    year = 2011;    
    
    get_years = True;
    while (get_years):
        if (0 == year % 4):
            if (seconds - SECONDS_PER_LEAP_YEAR) >= 0:
                year +=1;
                seconds = seconds - SECONDS_PER_LEAP_YEAR 
            else:
                get_years = False;
        else:
            if (seconds - SECONDS_PER_YEAR) >= 0:
                year +=1;
                seconds = seconds - SECONDS_PER_YEAR 
            else:
                get_years = False;        
        
        
    get_month = True;
    month = 1;
    while (get_month):
        seconds_in_month = days_per_month[month - 1] * SECONDS_PER_DAY;
        if ((0 == (year % 4)) and (2 == month)):
            seconds_in_month += SECONDS_PER_DAY;
             
        if ((seconds - seconds_in_month) >= 0):
            seconds = seconds - seconds_in_month;
            month += 1;
        else:
            get_month = False;
    
    get_day = True;
    day = 1;
    while (get_day):
        if (seconds - SECONDS_PER_DAY) >= 0:
            seconds = seconds - SECONDS_PER_DAY;
            day += 1;
        else:
            get_day = False;
    
    get_hour = True;
    hour = 0;
    while(get_hour):
        if (seconds - SECONDS_PER_HOUR) >= 0:
            hour += 1;
            seconds = seconds - SECONDS_PER_HOUR;
        else:
            get_hour = False;
    
    get_minute = True;
    minute = 0;
    while(get_minute):
        if (seconds - SECONDS_PER_MINUTE) >= 0:
            minute += 1;
            seconds = seconds - SECONDS_PER_MINUTE;
        else:
            get_minute = False;
            
    sec = seconds;
    return "%(1)02d-%(2)02d-%(3)02d  %(4)02d:%(5)02d:%(6)02d (EST)"  %{"1":month,"2":day,"3":year,"4":hour,"5":minute,"6":sec}
 
"""
Define some helper functions for creating HTML
"""
def trMsgHex( a, v, html):
    html.append("<tr><td style=\"text-align:right;font-weight:bold;\">%(1)s</td><td>x%(2)08X</td></tr>" %{"1":a, "2":v});
def trMsgLongHex( a, v1, v2, html):
    html.append("<tr><td style=\"text-align:right;font-weight:bold;\">%(1)s</td><td>x%(2)08X%(3)08X</td></tr>" %{"1":a, "2":v1, "3":v2});
def trMsgDec( a, v, html):
    html.append("<tr><td style=\"text-align:right;font-weight:bold;\">%(1)s</td><td>%(2)d</td></tr>" %{"1":a, "2":v});
def trMsgString( a, v, html):
    html.append("<tr><td style=\"text-align:right;font-weight:bold;\">%(1)s</td><td>%(2)s</td></tr>" %{"1":a, "2":v});    
def secondsToTimeString(seconds): 
    hours = seconds / 60 / 60;
    minutes = ((seconds / 60) % 60);
    secs = seconds % 60;

    result = "%(1)d:%(2)02d:%(3)02d" %{"1":hours,"2":minutes,"3":secs};
    
    return result

"""
Helper function to decode the faults
"""
def decode_faults(value,table,html):
    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (value & temp);
        if (temp):
            try:
                html.append("<tr><td></td><td>(x%(1)08X) %(2)s</td></tr>" %{"1":temp,"2":table[temp]});
            except:
                html.append("<tr><td></td><td>(x%(1)08X) NO_FAULT_INDICATION</td></tr>"%{"1":temp})
                
            
"""
This function creates the entire parsed faultlog file
"""            
def Create_Log_File(filename, data):

    outfile = open(filename, "w"); 
    
    """
    Create an array for holding the file lines
    """
    html = [];
    
    """
    Create the file header
    """
    html.append(("<html><head><title>RMP CCU Faultlog %s</title>\n"  %filename));
    html.append("\
    <style>\
    BODY, tr, td {\
      font-family: arial, sans;\
      font-size:11px;\
      background-color:#ffffff; \
      margin: 0px 5px 5px 30px;\
    }\
    td {\
      padding-right: 15px;\
    }\
    h1,h2,h3 {\
      font-family: tahoma;\
      color: darkred;\
      margin: 0px;\
    }\
    h2 {\
      font-size: 14px;\
    }\
    </style>");
    html.append("</head><body>\n")
    html.append("<h1>RMP CCU Faultlog</h1>\n")
    
    """
    Create the faultlog instance header table
    """
    html.append("<table>\n");
    trMsgString("Filename", filename, html);
    trMsgHex("Log Version", data[0],html);
    trMsgDec("Log Size Bytes", data[1],html);
    trMsgDec("Number of Entries", data[2],html);
    trMsgDec("Latest Entry", data[3],html);
    trMsgLongHex("Serial Number",data[4], data[5],html);
    trMsgDec("SP SW Build ID", data[6],html);
    trMsgDec("UIP SW Build ID", data[7],html);
    
    acc_time = secondsToTimeString(data[8]);
    trMsgString("Accumulated Time", acc_time,html);
    trMsgDec("Odometer (m)", data[9],html);
    trMsgDec("Power Cycles", data[10],html);
    html.append("</table>\n");
    
    html.append("<p>Faults are listed in the order they appear in the fault\n\
                log, not in the order in which they have occurred.</p>\n");
    
    
    """
    Append the entire raw faultlog
    """
    html.append("<!--  Raw Data From Log\n");
    raw_shorts = [0] * ((len(data) - 1) * 2);
    for i in range(0,(len(data) - 1)):
        raw_shorts[i * 2]     = (data[i] & 0xFFFF0000)>>16;
        raw_shorts[i * 2 + 1] = (data[i] & 0x0000FFFF);
        
    
    for i in range(0,len(raw_shorts)):    
        if ((i % 16) == 0):
            html.append("\n%03X: " %(i * 2));
            
        html.append("%04X " %raw_shorts[i]);
    
    html.append("\n-->");
    
    """
    Now start decoding each of the entries
    """
    fault_entries = [0] * MAX_FAULT_ENTRIES;
    
    for i in range(0,MAX_FAULT_ENTRIES):
        temp = [0] * NUMBER_OF_ITEMS_PER_ENTRY;
        for j in range(0,NUMBER_OF_ITEMS_PER_ENTRY):
            temp[j]= data[i * NUMBER_OF_ITEMS_PER_ENTRY + j + 11]
            
        fault_entries[i] = temp;
    
    for i in range(0,MAX_FAULT_ENTRIES):
        if ((i == data[3]) and (data[2])):
            html.append(("<h2 style='color:dark red'>Fault[ %d] (Latest Entry)</h2>\n" %i));
        else:
            html.append(("<h2>Fault[ %d]</h2>\n" %i));
        
        """
        Check if it is empty
        """
        empty = True;
        for j in range(0,NUMBER_OF_ITEMS_PER_ENTRY):
            if (0 != fault_entries[i][j]):
                empty = False; 
    
        if (empty):
            html.append("<i>empty</i>\n");
        else:
            """
            Create the faultlog entry table
            """
            html.append("<table>\n");
    
            timestamp = seconds_to_date(fault_entries[i][0]);
            trMsgString("Time Stamp", timestamp,html);
    
            runtimestamp = secondsToTimeString(fault_entries[i][1]);
            trMsgString("Runtime Stamp", runtimestamp,html);
            trMsgDec("Power Cycle", fault_entries[i][2],html);
    
            """
            Decode all the faults present. If we are in the MCU specific faults
            check the gpdata and decode that as well
            """
            for k in range(0,NUMBER_OF_FAULT_GROUPS):
                trMsgHex(fault_group_names[k], fault_entries[i][3+k],html);
                decode_faults(fault_entries[i][3+k], decode_list[k],html);
                
    
                if ((k == FAULTGROUP_MCU) and (fault_entries[i][3+k] != 0)):
                    if (0 == (fault_entries[i][3+k] & CCU_DETECTED_MCU_FAULT_MASK)):
                        decode_faults(fault_entries[i][11], mcu_specific_fault_decode,html);
    
            """
            Represent the gpdata in floating point by default
            """
            float_rep = convert_u32_to_float(fault_entries[i][11])
            html.append("<tr><td style=\"text-align:right;font-weight:bold;\">%(1)s</td><td>x%(2)08X %(3)f</td></tr>" 
                    % {"1":"Data[0]","2":fault_entries[i][11],"3":float_rep}); 
    
            float_rep = convert_u32_to_float(fault_entries[i][12])
            html.append("<tr><td style=\"text-align:right;font-weight:bold;\">%(1)s</td><td>x%(2)08X %(3)f</td></tr>" 
                    % {"1":"Data[1]","2":fault_entries[i][12],"3":float_rep}); 
                    
                    
            """
            Finished with this entry
            """
            html.append("<table>\n");
    
    """
    Finished with this log
    """
    html.append("</body></html>\n");
       
    """
    Write the outfile and close it
    """
    output = ''.join(html);
    outfile.write(output);
    outfile.close();
    
"""
Decode a FSW
"""    
def decode_fsw(fsw_array):

    """
    Parse the array into specific faultgroups
    """
    faultGroup = [0] * NUM_OF_FAULTGROUPS;
    
    faultGroup[FAULTGROUP_TRANSIENT]     = 0
    faultGroup[FAULTGROUP_CRITICAL]      =  (fsw_array[FSW_CRITICAL_FAULTS_INDEX] & FSW_CRITICAL_FAULTS_MASK) >> FSW_CRITICAL_FAULTS_SHIFT;
    faultGroup[FAULTGROUP_COMM]          =  (fsw_array[FSW_COMM_FAULTS_INDEX] & FSW_COMM_FAULTS_MASK) >> FSW_COMM_FAULTS_SHIFT;
    faultGroup[FAULTGROUP_SENSORS]       =  (fsw_array[FSW_SENSORS_FAULTS_INDEX] & FSW_SENSORS_FAULTS_MASK) >> FSW_SENSORS_FAULTS_SHIFT;    
    faultGroup[FAULTGROUP_BSA]           =  (fsw_array[FSW_BSA_FAULTS_INDEX] & FSW_BSA_FAULTS_MASK) >> FSW_BSA_FAULTS_SHIFT;
    faultGroup[FAULTGROUP_MCU]           =  (fsw_array[FSW_MCU_FAULTS_INDEX] & FSW_MCU_FAULTS_MASK) >> FSW_MCU_FAULTS_SHIFT;
    faultGroup[FAULTGROUP_ARCHITECTURE]  =  (fsw_array[FSW_ARCH_FAULTS_INDEX] & FSW_ARCH_FAULTS_MASK) >> FSW_ARCH_FAULTS_SHIFT;
    faultGroup[FAULTGROUP_INTERNAL]      =  (fsw_array[FSW_INTERNAL_FAULTS_INDEX] & FSW_INTERNAL_FAULTS_MASK) >> FSW_INTERNAL_FAULTS_SHIFT;

    """
    MCU specific faults get a special category because there is more information
    """
    mcu_specific_group = [];
    mcu_specific_group.append(fsw_array[4]);
    mcu_specific_group.append(fsw_array[5]);
    mcu_specific_group.append(fsw_array[6]);
    mcu_specific_group.append(fsw_array[7]);

    """
    Create a master list of present faults then check all the bits in each
    faultgroup and go to the dictionaries to get the names
    """
    faults_present = [];

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_CRITICAL] & temp);
        if (temp):
            faults_present.append(critical_fault_decode[temp]);

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_COMM] & temp);
        if (temp):
            faults_present.append(comm_fault_decode[temp]);

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_SENSORS] & temp);
        if (temp):
            faults_present.append(sensor_fault_decode[temp]);

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_BSA] & temp);
        if (temp):
            faults_present.append(bsa_fault_decode[temp]);

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_MCU] & temp);
        if (temp):
            faults_present.append(mcu_fault_decode[temp]);
            if (0 == (temp & CCU_DETECTED_MCU_FAULT_MASK)):
                for i in range(0,len(mcu_specific_group)):
                    for x in range(0,32):
                        temp = int(math.pow(2,x))
                        temp = (mcu_specific_group[i] & temp);
                        if (temp):
                            faults_present.append(mcu_specific_fault_decode[temp]);

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_ARCHITECTURE] & temp);
        if (temp):
            faults_present.append(arch_fault_decode[temp]);

    for x in range(0,32):
        temp = int(math.pow(2,x))
        temp = (faultGroup[FAULTGROUP_INTERNAL] & temp);
        if (temp):
            faults_present.append(internal_fault_decode[temp]);


    return faults_present    

from segway_msgs.msg import Faultlog
import rclpy
from rclpy.node import Node

class FaultlogParserNode(Node):
    
        def __init__(self):
            super().__init__('faultlog_parser')
            self.faultlog_subscriber = self.create_subscription(Faultlog, 'segway/feedback/faultlog', self.faultlog_callback, 10)
    
        def faultlog_callback(self, msg):
            rclpy.logging.get_logger('faultlog_parser').info('Received faultlog')
            faultlog_array = msg
            FaultlogParser(faultlog_array)


def main(args=None):

    """
    Initialize the node
    """
    rclpy.init(args=args)
    faultlog_parser = FaultlogParserNode()
    rclpy.spin(faultlog_parser)
    rclpy.shutdown()


if __name__ == '__main__':
    main()