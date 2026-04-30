import re
import json
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
import random
import requests
from bs4 import BeautifulSoup
import os

class CampusChatbot:
    def __init__(self):
        self.intents = self.load_intents()
        self.knowledge_base = self.load_knowledge_base()
        self.fallback_staff_data = self.load_fallback_staff()
        self._staff_cache = None
        self._staff_cache_time = 0
        self._staff_cache_ttl = 60 * 60 * 24
        self._db_path = os.path.join(os.path.dirname(__file__), 'campus_assistant.db')
    
    def load_fallback_staff(self):
        """Load fallback staff data when web scraping fails.
        Based on IARE structure with comprehensive faculty details.
        """
        return [
            # Leadership & Principal
            {'name': 'Dr. A Govardhan', 'designation': 'Professor & Principal', 'email': 'principal@iare.ac.in', 'phone': '+91 91546 78975', 'department': 'Administration', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            
            # CSE Department (Computer Science & Engineering)
            {'name': 'Dr. S Ramachandram', 'designation': 'Professor & HOD CSE', 'email': 'hod.cse@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. R Tejaswini', 'designation': 'Assistant Professor', 'email': 'tejaswini@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {
                'name': 'Dr. P Ramadevi', 
                'designation': 'Associate Professor', 
                'email': 'p.ramadevi@iare.ac.in', 
                'phone': '', 
                'department': 'CSE Cyber Security', 
                'profile_url': 'https://www.iare.ac.in',
                'faculty_id': 'IARE10974',
                'experience': '16 Years, 4 Months',
                'experience_iare': '3 Years, 5 Months',
                'dob': 'Thursday, August 1, 1974',
                'employment_status': 'Full Time, JNTUH Ratified',
                'jntuh_id': '83150331-223450',
                'aicte_id': '1-2296823630',
                'ug_degree': 'IEI, Calcutta, West Bengal, 2000',
                'pg_degree': 'University of Madras, Chennai, Tamil Nadu, 2002',
                'phd_degree': 'Jawaharlal Nehru Technological University Hyderabad, TS, 2016',
                'qualification': 'Ph.D',
                'specialization': 'Applied Electronics, Ad hoc Wireless Networks',
                'vidwan_link': 'https://iare.irins.org/profile/284097'
            },
            {
                'name': 'Ms. Sahana Susheela',
                'designation': 'Assistant Professor',
                'email': 'sahanasusheela@iare.ac.in',
                'phone': '',
                'department': 'CSE Cyber Security',
                'profile_url': 'https://www.iare.ac.in',
                'faculty_id': 'IARE11104',
                'experience': '2 Years, 6 Months',
                'experience_iare': '2 Years, 6 Months',
                'dob': 'Tuesday, July 23, 1996',
                'employment_status': 'Full Time',
                'jntuh_id': '0531-231013-094106',
                'aicte_id': '1-43710283454',
                'ug_degree': 'Visvesvaraya Technological University, Belgum, Karnataka, 2018',
                'pg_degree': 'Visvesvaraya Technological University, Belgum, Karnataka, 2022',
                'phd_degree': '-',
                'qualification': 'M.Tech',
                'specialization': 'Data Mining',
                'vidwan_link': 'https://iare.irins.org/profile/446996',
                'youtube_link': 'https://www.youtube.com/channel/UCrN2YGajq0ITaokeOn2LEpQ'
            },
            {
                'name': 'Dr. Mahammad Rafi D',
                'designation': 'Associate Professor',
                'email': 'dr.mahammad@iare.ac.in',
                'phone': '',
                'department': 'CSE Cyber Security',
                'profile_url': 'https://www.iare.ac.in',
                'faculty_id': 'IARE11118',
                'experience': '17 Years, 2 Months',
                'experience_iare': '2 Years, 3 Months',
                'dob': 'Monday, July 7, 1980',
                'employment_status': 'Full Time',
                'jntuh_id': '9729-150414-164535',
                'aicte_id': '1-43710283496',
                'ug_degree': 'Jawaharlal Nehru Technological University, Hyderabad, TS, 2005',
                'pg_degree': 'Jawaharlal Nehru Technological University, Hyderabad, TS, 2008',
                'phd_degree': 'Veltech (Deemed to be University), Chennai, Tamil Nadu, 2020',
                'qualification': 'Ph.D',
                'specialization': 'Data Mining',
                'vidwan_link': 'https://iare.irins.org/profile/464888/MjE3NTM4',
                'youtube_link': 'https://www.youtube.com/playlist?list=PLzkMouYverAL6Oxhx10g_ctFCrM5tlcPj'
            },
            {'name': 'Dr. B Padmaja Rani', 'designation': 'Professor', 'email': 'padmaja@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. S Sreenatha Reddy', 'designation': 'Professor', 'email': 'sreenatha@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. D Haritha', 'designation': 'Associate Professor', 'email': 'haritha@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. K Venkatesh', 'designation': 'Assistant Professor', 'email': 'venkatesh.cse@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. M Asha Rani', 'designation': 'Associate Professor', 'email': 'asharani@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. P Swathi', 'designation': 'Assistant Professor', 'email': 'swathi.cse@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. K Srujan Raju', 'designation': 'Professor', 'email': 'srujanraju@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. N Ravi Kumar', 'designation': 'Assistant Professor', 'email': 'ravikumar.cse@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Ms. L Priyanka', 'designation': 'Assistant Professor', 'email': 'priyanka.cse@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. V Sumalatha', 'designation': 'Associate Professor', 'email': 'sumalatha@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. S Karthik', 'designation': 'Assistant Professor', 'email': 'karthik.cse@iare.ac.in', 'phone': '', 'department': 'CSE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            
            # CSE - AI & ML
            {'name': 'Dr. T Santhi Sri', 'designation': 'Professor & HOD CSE (AI&ML)', 'email': 'hod.aiml@iare.ac.in', 'phone': '', 'department': 'CSE-AIML', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. A Ananda Rao', 'designation': 'Associate Professor', 'email': 'ananda.aiml@iare.ac.in', 'phone': '', 'department': 'CSE-AIML', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. K Madhavi', 'designation': 'Assistant Professor', 'email': 'madhavi.aiml@iare.ac.in', 'phone': '', 'department': 'CSE-AIML', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            
            # CSE - Data Science
            {'name': 'Dr. K Rajendra Prasad', 'designation': 'Professor & HOD CSE (DS) and (CS)', 'email': 'hod.ds@iare.ac.in', 'phone': '', 'department': 'CSE-DS', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {
                'name': 'Dr. K Rajendra Prasad',
                'designation': 'Professor & Head',
                'email': 'dr.rajendraprasad@iare.ac.in',
                'phone': '',
                'department': 'CSE Data Science',
                'profile_url': 'https://www.iare.ac.in',
                'faculty_id': 'IARE11023',
                'experience': '25 Years, 8 Months',
                'experience_iare': '9 Years, 9 Months',
                'dob': 'Tuesday, April 5, 1977',
                'employment_status': 'Full Time',
                'jntuh_id': '2605-160310-131957',
                'aicte_id': '1-2908 8913 93',
                'ug_degree': 'Jawaharlal Nehru Technological University, Hyderabad, TS, 1999',
                'pg_degree': 'Visvesvaraya Technological University, Belgum, Karnataka, 2004',
                'phd_degree': 'Jawaharlal Nehru Technological University, Anantapur, AP, 2015',
                'qualification': 'Ph.D',
                'specialization': 'Data Mining, Pattern Recognition, Artificial Intelligence, Speech and Signal Processing, Soft Computing Techniques, Information Retrieval Techniques, Data Visualization Methods',
                'vidwan_link': 'https://iare.irins.org/profile/357633',
                'youtube_link': 'https://www.youtube.com/channel/UCrN2YGajq0ITaokeOn2LEpQ'
            },
            {
                'name': 'Dr. G Ganapathi Rao',
                'designation': 'Assistant Professor',
                'email': 'g.ganapathirao@iare.ac.in',
                'phone': '',
                'department': 'CSE Data Science',
                'profile_url': 'https://www.iare.ac.in',
                'faculty_id': 'IARE11085',
                'experience': '8 Years, 6 Months',
                'experience_iare': '2 Years, 7 Months',
                'dob': 'Tuesday, June 15, 1982',
                'employment_status': 'Full Time',
                'jntuh_id': '8582-230925-145827',
                'aicte_id': '',
                'ug_degree': 'Acharya Nagarjuna University, Guntur, AP, 2003',
                'pg_degree': 'Jawaharlal Nehru Technological University, Hyderabad, TS, 2011',
                'phd_degree': 'Andhra University, Visakhapatnam, AP, 2017',
                'qualification': 'Ph.D',
                'specialization': 'Data Mining',
                'vidwan_link': 'https://iare.irins.org/profile/292763',
                'youtube_link': 'https://www.youtube.com/channel/UCrN2YGajq0ITaokeOn2LEpQ'
            },
            {'name': 'Dr. M Vijaya Kumar', 'designation': 'Associate Professor', 'email': 'vijayakumar.ds@iare.ac.in', 'phone': '', 'department': 'CSE-DS', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {
                'name': 'Ms. S Bhagyashree',
                'designation': 'Assistant Professor',
                'email': 's.bhagyashree@iare.ac.in',
                'phone': '',
                'department': 'CSE Data Science',
                'profile_url': 'https://www.iare.ac.in/?q=node/4971',
                'faculty_id': 'IARE11120',
                'experience': '2 Years, 3 Months',
                'experience_iare': '2 Years, 3 Months',
                'dob': 'Friday, August 25, 2000',
                'employment_status': 'Full Time',
                'jntuh_id': '1019-240108-111214',
                'aicte_id': '1-43704980561',
                'ug_degree': 'Visvesvaraya Technological University, Belgum, Karnataka, 2021',
                'pg_degree': 'Visvesvaraya Technological University, Belgum, Karnataka, 2023',
                'phd_degree': '-',
                'qualification': 'M.Tech',
                'specialization': 'Computer Networks',
                'vidwan_link': 'https://iare.irins.org/profile/474144/MjE3NTM4'
            },
            {
                'name': 'Ms. P Aswani',
                'designation': 'Assistant Professor',
                'email': 'p.aswani@iare.ac.in',
                'phone': '',
                'department': 'CSE Data Science',
                'profile_url': 'https://www.iare.ac.in',
                'faculty_id': 'IARE11069',
                'experience': '8 Years, 8 Months',
                'experience_iare': '2 Years, 9 Months',
                'dob': 'Sunday, March 8, 1987',
                'employment_status': 'Full Time',
                'jntuh_id': '1649-150413-151727',
                'aicte_id': '1-26477590291',
                'ug_degree': 'Jawaharlal Nehru Technological University, Hyderabad, TS, 2008',
                'pg_degree': 'Jawaharlal Nehru Technological University, Hyderabad, TS, 2012',
                'phd_degree': '-',
                'qualification': 'M.Tech',
                'specialization': 'Software Engineering',
                'vidwan_link': 'https://iare.irins.org/profile/393990',
                'youtube_link': 'https://www.youtube.com/channel/UCrN2YGajq0ITaokeOn2LEpQ'
            },
            
            # ECE Department (Electronics & Communication Engineering)
            {'name': 'Dr. M Madhavi Latha', 'designation': 'Professor & HOD ECE', 'email': 'hod.ece@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. K Kishan Rao', 'designation': 'Professor', 'email': 'kishanrao@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. P Chandra Sekhar', 'designation': 'Associate Professor', 'email': 'chandrasekhar@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. G Hymavathi', 'designation': 'Assistant Professor', 'email': 'hymavathi@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. N Satyanarayana', 'designation': 'Associate Professor', 'email': 'satya.ece@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. R Suresh', 'designation': 'Assistant Professor', 'email': 'suresh.ece@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Ms. S Kavitha', 'designation': 'Assistant Professor', 'email': 'kavitha.ece@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. B Rajesh Kumar', 'designation': 'Professor', 'email': 'rajeshkumar@iare.ac.in', 'phone': '', 'department': 'ECE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            
            # EEE Department (Electrical & Electronics Engineering)
            {'name': 'Dr. K Srinivas', 'designation': 'Professor & HOD EEE', 'email': 'hod.eee@iare.ac.in', 'phone': '', 'department': 'EEE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. M Sailaja', 'designation': 'Associate Professor', 'email': 'sailaja@iare.ac.in', 'phone': '', 'department': 'EEE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. T Prakash', 'designation': 'Assistant Professor', 'email': 'prakash.eee@iare.ac.in', 'phone': '', 'department': 'EEE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. V Ramesh', 'designation': 'Associate Professor', 'email': 'ramesh.eee@iare.ac.in', 'phone': '', 'department': 'EEE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. A Lakshmi', 'designation': 'Assistant Professor', 'email': 'lakshmi.eee@iare.ac.in', 'phone': '', 'department': 'EEE', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            
            # MECH Department (Mechanical Engineering)
            {'name': 'Dr. P V V Satyanarayana', 'designation': 'Professor & HOD MECH', 'email': 'hod.mech@iare.ac.in', 'phone': '', 'department': 'MECH', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. K Hemachandra Reddy', 'designation': 'Professor', 'email': 'hemachandra@iare.ac.in', 'phone': '', 'department': 'MECH', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. G Mallikarjuna', 'designation': 'Assistant Professor', 'email': 'mallikarjuna@iare.ac.in', 'phone': '', 'department': 'MECH', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            {'name': 'Dr. S Narayana', 'designation': 'Associate Professor', 'email': 'narayana.mech@iare.ac.in', 'phone': '', 'department': 'MECH', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. P Srinivas', 'designation': 'Assistant Professor', 'email': 'srinivas.mech@iare.ac.in', 'phone': '', 'department': 'MECH', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            
            # CIVIL Department
            {'name': 'Dr. S Vijaya Kumar', 'designation': 'Professor & HOD CIVIL', 'email': 'hod.civil@iare.ac.in', 'phone': '', 'department': 'CIVIL', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. M Ravi Teja', 'designation': 'Associate Professor', 'email': 'raviteja@iare.ac.in', 'phone': '', 'department': 'CIVIL', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Mr. K Praveen Kumar', 'designation': 'Assistant Professor', 'email': 'praveen.civil@iare.ac.in', 'phone': '', 'department': 'CIVIL', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            
            # IT Department (Information Technology)
            {'name': 'Dr. N Srinivasa Rao', 'designation': 'Professor & HOD IT', 'email': 'hod.it@iare.ac.in', 'phone': '', 'department': 'IT', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. R Swathi', 'designation': 'Associate Professor', 'email': 'swathi.it@iare.ac.in', 'phone': '', 'department': 'IT', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. V Mounika', 'designation': 'Assistant Professor', 'email': 'mounika.it@iare.ac.in', 'phone': '', 'department': 'IT', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
            
            # Aeronautical Engineering
            {'name': 'Dr. M Srinivasa Rao', 'designation': 'Professor & HOD AERO', 'email': 'hod.aero@iare.ac.in', 'phone': '', 'department': 'AERO', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. K Chandra Sekhara Reddy', 'designation': 'Professor', 'email': 'chandrasekhara@iare.ac.in', 'phone': '', 'department': 'AERO', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            
            # MBA Department
            {'name': 'Dr. P Srinivasa Rao', 'designation': 'Professor & HOD MBA', 'email': 'hod.mba@iare.ac.in', 'phone': '', 'department': 'MBA', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. M Bhavani', 'designation': 'Associate Professor', 'email': 'bhavani.mba@iare.ac.in', 'phone': '', 'department': 'MBA', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            
            # Science & Humanities
            {'name': 'Dr. K Mallikarjuna Rao', 'designation': 'Professor & HOD S&H', 'email': 'hod.sh@iare.ac.in', 'phone': '', 'department': 'S&H', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Dr. B Srinivasa Rao', 'designation': 'Associate Professor', 'email': 'srinivas.sh@iare.ac.in', 'phone': '', 'department': 'S&H', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'Ph.D', 'specialization': ''},
            {'name': 'Ms. L Anuradha', 'designation': 'Assistant Professor', 'email': 'anuradha.sh@iare.ac.in', 'phone': '', 'department': 'S&H', 'profile_url': 'https://www.iare.ac.in', 'faculty_id': '', 'experience': '', 'qualification': 'M.Tech', 'specialization': ''},
        ]
        
    def load_intents(self):
        """Load intent patterns and responses"""
        return {
            'greeting': {
                'patterns': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'],
                'responses': [
                    "Hello! I'm your Campus Assistant. How can I help you today?",
                    "Hi there! Welcome to Campus Assistant. What would you like to know?",
                    "Hey! I'm here to help with campus information. What's your question?"
                ]
            },
            'attendance': {
                'patterns': ['attendance', 'my attendance', 'check attendance', 'attendance percentage', 'show attendance', 'how much attendance', 'attendance status', 'classes attended', 'attendance report'],
                'responses': [
                    """📊 **Your Attendance Report — Current Semester**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """**📚 Theory Subjects:**\n\n"""
                    """**1. Theory of Computation** (ACSD31) — CORE\n"""
                    """   • Conducted: 68 | Attended: 59 | **Attendance: 86.76%** ✅ Satisfactory\n\n"""
                    """**2. Penetration Testing and Cyber Operations** (ACCD10) — CORE\n"""
                    """   • Conducted: 68 | Attended: 63 | **Attendance: 92.65%** ✅ Satisfactory\n\n"""
                    """**3. Software Project Management** (ACSD25) — PE-II\n"""
                    """   • Conducted: 55 | Attended: 50 | **Attendance: 90.91%** ✅ Satisfactory\n\n"""
                    """**4. Cyber Physical Systems** (ACAD09) — PE-III\n"""
                    """   • Conducted: 52 | Attended: 46 | **Attendance: 88.46%** ✅ Satisfactory\n\n"""
                    """**5. Computer Graphics and Multimedia Systems** (AITD18) — OE-I\n"""
                    """   • Conducted: 48 | Attended: 42 | **Attendance: 87.50%** ✅ Satisfactory\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """**🔬 Laboratory Subjects:**\n\n"""
                    """**6. Computer System Internals and Linux Laboratory** (ACSD41) — CORE\n"""
                    """   • Conducted: 43 | Attended: 22 | **Attendance: 51.16%** 🔴 Shortage\n\n"""
                    """**7. Penetration Testing and Cyber Operations Laboratory** (ACCD18) — CORE\n"""
                    """   • Conducted: 38 | Attended: 38 | **Attendance: 100%** ✅ Satisfactory\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """**🛠️ Skill Subjects:**\n\n"""
                    """**8. AI Specialist** (ACSD44) — SKILL\n"""
                    """   • Conducted: 39 | Attended: 27 | **Attendance: 69.23%** 🟡 Condonation\n\n"""
                    """**9. Engineering Development Project** (ACSD45) — SKILL\n"""
                    """   • Conducted: 50 | Attended: 35 | **Attendance: 70.00%** 🟡 Condonation\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """📈 **Overall Attendance Summary:**\n"""
                    """• **Total Classes Conducted:** 461\n"""
                    """• **Total Classes Attended:** 382\n"""
                    """• **Overall Attendance: 82.86%**\n\n"""
                    """⚠️ **Alerts:**\n"""
                    """• 🔴 **Shortage** in Computer System Internals and Linux Lab (51.16%) — Immediate attention needed!\n"""
                    """• 🟡 **Condonation** in AI Specialist (69.23%) and Engineering Development Project (70%)\n\n"""
                    """💡 **Note:** Minimum 75% attendance is required to be eligible for end semester exams.\n"""
                    """📧 For attendance queries, contact your class coordinator."""
                ]
            },
            'about_bot': {
                'patterns': ['who are you', 'what are you', 'tell me about yourself', 'about you', 'introduce yourself', 'what can you do', 'your purpose', 'help me', 'what do you know'],
                'responses': [
                    """👋 Hello! I'm the **Campus Assistant AI Chatbot** for IARE (Institute of Aeronautical Engineering).

🤖 **About Me:**
• I'm an AI-powered virtual assistant designed to help students, faculty, and visitors
• Available 24/7 to answer your campus-related questions
• Powered by Natural Language Processing to understand your queries

📚 **What I Can Help You With:**

1️⃣ **Admissions** - Application process, eligibility, deadlines, entrance exams
2️⃣ **Placements** - Job statistics, top recruiters, training programs
3️⃣ **Academics** - Exam schedules, results, credits, timetables
4️⃣ **Hostel & Accommodation** - Facilities, fees, application process
5️⃣ **Library** - Hours, resources, book issuing, digital library
6️⃣ **Fees & Scholarships** - Tuition fees, payment, financial aid
7️⃣ **Events & Activities** - Fests, workshops, competitions, seminars
8️⃣ **Faculty & Departments** - Contact info, consultation hours
9️⃣ **Transport** - Bus routes, timings, fees
🔟 **WiFi & IT** - Network access, login issues, helpdesk
1️⃣1️⃣ **Labs & Facilities** - Lab hours, equipment, sports facilities
1️⃣2️⃣ **Contact Info** - Phone numbers, email addresses, office locations
1️⃣3️⃣ **General Info** - College timings, holidays, policies

💡 **How to Use Me:**
• Just type your question naturally (e.g., "What are the library hours?")
• I'll detect what you're asking about and provide accurate information
• You can also click on suggested questions below the chat

🎯 **My Goal:**
To make campus information easily accessible and save your time by providing instant, accurate answers!

Try asking me something like:
• "Tell me about admissions"
• "What are placement statistics?"
• "Library hours?"
• "How to apply for hostel?"

I'm here to help! What would you like to know? 😊""",
                    """🤖 **I'm Your IARE Campus Assistant AI!**

Built specifically for IARE to provide 24/7 campus support.

**My Capabilities:**
✅ Answer questions about admissions, placements, academics
✅ Provide information on hostel, library, and campus facilities
✅ Help with exam schedules, fees, and scholarships
✅ Guide you about events, transport, and contact details
✅ Understand natural language - talk to me like a human!

**What Makes Me Special:**
🧠 Smart AI that learns and improves
⚡ Instant responses - no waiting
🎯 Accurate campus-specific information
💬 Friendly and easy to talk to
📊 Backed by a comprehensive knowledge base

**I'm powered by:**
• Natural Language Processing (NLP)
• Pattern matching algorithms
• Campus knowledge database
• Google Gemini AI (for complex queries)

Ask me anything about campus - I'm here to help! 🚀"""
                ]
            },
            'admission': {
                'patterns': ['admission', 'admissions', 'apply', 'application', 'how to join', 'enrollment', 'entrance'],
                'responses': [
                    "For admissions, you can visit the admissions office or apply online through our portal. Key dates: Applications open in May, entrance exams in June.",
                    "Admission process includes: 1) Online application 2) Entrance exam 3) Counseling 4) Document verification. Visit admissions.iare.ac.in for details."
                ]
            },
            'placements': {
                'patterns': ['placement', 'placements', 'job', 'career', 'recruitment', 'companies', 'package'],
                'responses': [
                    "Our placement cell has partnerships with 200+ companies. Average package: 6 LPA, Highest: 32 LPA. Training programs start from 3rd year.",
                    "Placement highlights: Top recruiters include TCS, Infosys, Amazon, Microsoft. Contact: placements@iare.ac.in"
                ]
            },
            'hostel': {
                'patterns': ['hostel', 'accommodation', 'room', 'mess', 'food', 'stay'],
                'responses': [
                    "Hostel facilities: Separate boys and girls hostels, 24/7 security, WiFi, gym, mess with quality food. Fees: ₹80,000/year.",
                    "Hostel amenities include AC/Non-AC rooms, laundry, recreation room, and medical facilities. Apply through student portal."
                ]
            },
            'exam': {
                'patterns': ['exam', 'examination', 'test', 'when is exam', 'exam schedule', 'exam date', 'exam timing', 'upcoming exam', 'end sem', 'end semester'],
                'responses': [
                    """📅 **Upcoming End Semester Examinations — BT23 Regulations**\n\n"""
                    """⏰ **Timings:**\n"""
                    """• **FN (Forenoon):** 10:15 AM to 12:15 PM\n"""
                    """• **AN (Afternoon):** 02:00 PM to 04:00 PM\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **31-Mar-2026 (Tuesday)**\n\n"""
                    """**🌅 FN Session (10:15 AM – 12:15 PM):**\n"""
                    """| Code | Subject | Branch |\n"""
                    """| AMTD09 | Waste to Energy Conversion Techniques | AE, EEE |\n"""
                    """| AITD31 | E-Commerce | CSE, CSE(AI&ML), IT |\n"""
                    """| ACAD38 | Deep Learning Paradigms for Computer Vision | CSE(CS), CSE(DS) |\n"""
                    """| AFED63 | Electrical Vehicle | ECE |\n"""
                    """| AAED25 | Computational Aerodynamics and Turbulence Modeling | AE |\n\n"""
                    """**🌇 AN Session (02:00 PM – 04:00 PM):**\n"""
                    """| Code | Subject | Branch |\n"""
                    """| ACSD31 | Theory of Computation | CSE, CSE(CS), IT |\n"""
                    """| ACDD11 | Cloud Computing | CSE(AI&ML) |\n"""
                    """| AITD04 | Computer Networks | CSE(DS) |\n"""
                    """| AECD90 | VLSI Design | ECE |\n"""
                    """| AMDD30 | Heat Transfer | ME |\n"""
                    """| AEED36 | Sustainable Energy Systems | EEE |\n"""
                    """| ACED25 | Design of Steel Structures | CE |\n"""
                    """| AAED26 | Finite Element Methods | AE |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **01-Apr-2026 (Wednesday)**\n\n"""
                    """**🌅 FN Session (10:15 AM – 12:15 PM):**\n"""
                    """| Code | Subject | Branch |\n"""
                    """| ACSD32 | Neural Computing and Deep Learning | CSE, IT |\n"""
                    """| ACDD06 | Data Mining and Warehousing | CSE(AI&ML) |\n"""
                    """| ACAD06 | Machine Learning Algorithms | CSE(DS) |\n"""
                    """| ACCD10 | Penetration Testing and Cyber Operations | CSE(CS) |\n"""
                    """| AECD31 | Digital Signal and Image Processing | ECE |\n"""
                    """| AMED11 | Computational Fluid Dynamics for ME Applications | ME |\n"""
                    """| AEED25 | Power System Analysis | EEE |\n"""
                    """| ACED26 | Foundation Engineering | CE |\n"""
                    """| AAED27 | Aircraft Systems and Control | AE |\n\n"""
                    """**🌇 AN Session (02:00 PM – 04:00 PM):**\n"""
                    """| Code | Subject | Branch |\n"""
                    """| AITD22 | Software Testing Methodologies | CSE |\n"""
                    """| ACCD05 | Computer Vision | CSE(AI&ML) |\n"""
                    """| AITD18 | Computer Graphics and Multimedia Systems | CSE(CS), CSE(DS) |\n"""
                    """| ACSD39 | Cyber Laws and Security | IT |\n"""
                    """| AECD34 | Digital Design Through VHDL | ECE |\n"""
                    """| AMED13 | Engineering Tribology | ME |\n"""
                    """| AEED26 | Electric Drives and Static Control | EEE |\n"""
                    """| ACED27 | Estimation, Costing and Valuation | CE |\n"""
                    """| AAED36 | Unmanned Air Vehicles | AE |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **02-Apr-2026 (Thursday)**\n\n"""
                    """**🌅 FN Session (10:15 AM – 12:15 PM):**\n"""
                    """| Code | Subject | Branch |\n"""
                    """| ACSD47 | Large Language Models | CSE |\n"""
                    """| ACAD12 | Fuzzy Logic and Inference Systems | CSE(AI&ML) |\n"""
                    """| AITD11 | Natural Language Processing | CSE(DS), IT |\n"""
                    """| ACSD25 | Software Project Management | CSE(CS) |\n"""
                    """| AECD40 | Digital Signal Processors and Architectures | ECE |\n"""
                    """| AMED38 | Unconventional Machining Process | ME |\n"""
                    """| AEED33 | HVDC Transmission | EEE |\n"""
                    """| ACED13 | Air Pollution and Control | CE |\n"""
                    """| ACAD20 | Machine Learning Techniques and Practices | AE, ECE, ME, EEE, CE |\n\n"""
                    """**🌇 AN Session (02:00 PM – 04:00 PM):**\n"""
                    """| Code | Subject | Branch |\n"""
                    """| ACDD18 | Business Intelligence | CSE, CSE(AI&ML) |\n"""
                    """| ACAD08 | Information Retrieval System | CSE(DS) |\n"""
                    """| ACAD09 | Cyber Physical Systems | CSE |\n"""
                    """| AITD16 | Agile Development and Scrum Practices | IT |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """⚠️ **Important Reminders:**\n"""
                    """• Always carry your **ID card** and **hall ticket**\n"""
                    """• No electronic devices allowed in exam hall\n"""
                    """• Report to exam hall **15 minutes** before start time\n"""
                    """• Check student portal regularly for updates\n\n"""
                    """📧 For queries, contact your department office."""
                ]
            },
            'marks': {
                'patterns': ['my marks', 'show marks', 'grades', 'my grades', 'score', 'my score', 'results', 'my results', 'mark sheet', 'grade sheet', 'sem results', 'semester results', 'cgpa', 'sgpa', 'gpa', 'academic results'],
                'responses': [
                    """🎓 **Semester Results — Academic Performance**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📘 **I SEMESTER**\n\n"""
                    """| Code | Subject | Grade | Credits |\n"""
                    """| AHSD02 | Matrices and Calculus | C (5) | 4.00 |\n"""
                    """| AHSD03 | Engineering Chemistry | C (5) | 3.00 |\n"""
                    """| AHSD07 | Applied Physics | B (6) | 3.00 |\n"""
                    """| ACSD01 | Object Oriented Programming | C (5) | 3.00 |\n"""
                    """| AHSD09 | Applied Physics Laboratory | A (8) | 1.00 |\n"""
                    """| ACSD02 | OOP with Java Laboratory | B+ (7) | 2.00 |\n"""
                    """| AHSD05 | Engineering Chemistry Lab | A+ (9) | 1.00 |\n"""
                    """| AMED03 | Engineering Graphics | A+ (9) | 2.00 |\n"""
                    """| ACSD04 | Mobile Applications Development | A (8) | 1.00 |\n"""
                    """| AHSD06 | Environmental Science | — | 0.00 |\n"""
                    """**Total Credits: 20 | SGPA: 6.25 | CGPA: 6.25**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📗 **II SEMESTER**\n\n"""
                    """| Code | Subject | Grade | Credits |\n"""
                    """| AHSD01 | Professional Communication | B (6) | 3.00 |\n"""
                    """| AHSD08 | Differential Equations & Vector Calculus | B (6) | 4.00 |\n"""
                    """| ACSD05 | Essentials of Problem Solving | B (6) | 3.00 |\n"""
                    """| AEED01 | Elements of Electrical & Electronics Engg | C (5) | 3.00 |\n"""
                    """| AHSD04 | Professional Communication Lab | A+ (9) | 1.00 |\n"""
                    """| ACSD06 | Programming for Problem Solving Lab | S (10) | 2.00 |\n"""
                    """| AMED02 | Manufacturing Practice | — | — |\n"""
                    """| AEED03 | Electrical & Electronics Engg Lab | A (8) | 1.00 |\n"""
                    """| ACSD03 | Essentials of Innovation | S (10) | 1.00 |\n"""
                    """| AHSD10 | Gender Sensitization | C (5) | 0.00 |\n"""
                    """**Total Credits: 20 | SGPA: 6.70 | CGPA: 6.48**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📙 **III SEMESTER**\n\n"""
                    """| Code | Subject | Grade | Credits |\n"""
                    """| AHSD11 | Probability and Statistics | B (6) | 4.00 |\n"""
                    """| AECD04 | Computer System Architecture | B (6) | 3.00 |\n"""
                    """| ACSD08 | Data Structures | B (6) | 3.00 |\n"""
                    """| ACSD09 | Operating Systems | C (5) | 3.00 |\n"""
                    """| ACCD01 | Essentials of Cyber Security | B (6) | 3.00 |\n"""
                    """| ACSD10 | Operating Systems Laboratory | A+ (9) | 1.00 |\n"""
                    """| ACSD11 | Data Structures Laboratory | A (8) | 1.00 |\n"""
                    """| AITD02 | Programming with Objects Lab | S (10) | 1.00 |\n"""
                    """| ACSD12 | Prototype and Design Building | A+ (9) | 1.00 |\n"""
                    """**Total Credits: 20 | SGPA: 6.45 | CGPA: 6.47**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📕 **IV SEMESTER**\n\n"""
                    """| Code | Subject | Grade | Credits |\n"""
                    """| ACSD13 | Design and Analysis of Algorithms | B+ (7) | 3.00 |\n"""
                    """| AITD03 | Database Management Systems | B (6) | 3.00 |\n"""
                    """| AITD04 | Computer Networks | B (6) | 3.00 |\n"""
                    """| ACSD15 | Object Oriented Software Engineering | B (6) | 3.00 |\n"""
                    """| ACCD02 | Ethical Hacking | B+ (7) | 3.00 |\n"""
                    """| ACSD16 | Design & Analysis of Algorithms Lab | A+ (9) | 1.00 |\n"""
                    """| AECD03 | Computer Networks Laboratory | A+ (9) | 1.00 |\n"""
                    """| AITD05 | DBMS Laboratory | A+ (9) | 1.00 |\n"""
                    """| ACSD18 | DevOps Engineering | S (10) | 2.00 |\n"""
                    """| AFID02 | Field Practicum / Internship | A+ (9) | 0.00 |\n"""
                    """**Total Credits: 20 | SGPA: 7.15 | CGPA: 6.64**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📓 **V SEMESTER**\n\n"""
                    """| Code | Subject | Grade | Credits |\n"""
                    """| ACSD19 | Data Mining and Machine Learning | B (6) | 3.00 |\n"""
                    """| ACSD14 | Web System Engineering | B+ (7) | 3.00 |\n"""
                    """| ACSD21 | Artificial Intelligence | B+ (7) | 3.00 |\n"""
                    """| ACCD04 | Information Security Management | F (0) | 3.00 | 🔴 FAIL\n"""
                    """| ACCD08 | Principles of IoT | B (6) | 3.00 |\n"""
                    """| ACSD26 | Artificial Intelligence Laboratory | A+ (9) | 1.00 |\n"""
                    """| ACSD17 | Web System Engineering Laboratory | A+ (9) | 1.00 |\n"""
                    """| ACSD29 | Engineering Design Project | A+ (9) | 1.00 |\n"""
                    """| ACSD30 | Java Full Stack Development | S (10) | 2.00 |\n"""
                    """**Total Credits: 20 | SGPA: 6.25 | CGPA: 6.56**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """📊 **Cumulative Performance Summary:**\n"""
                    """| Semester | SGPA | CGPA |\n"""
                    """| I | 6.25 | 6.25 |\n"""
                    """| II | 6.70 | 6.48 |\n"""
                    """| III | 6.45 | 6.47 |\n"""
                    """| IV | 7.15 | 6.64 |\n"""
                    """| V | 6.25 | 6.56 |\n\n"""
                    """⚠️ **Alert:** 🔴 FAIL in Information Security Management (ACCD04) — Sem V\n\n"""
                    """💡 **Current CGPA: 6.56** | Total Credits Earned: 100\n"""
                    """📧 For result queries, contact your department office."""
                ]
            },
            'internal_marks': {
                'patterns': ['mid marks', 'internal marks', 'cia marks', 'mid term marks', 'cia', 'mid 1', 'mid 2', 'mid', 'internal', 'internals', 'aat marks', 'current marks', 'mid exam marks', 'cia 1', 'cia 2', 'cie marks', 'cie'],
                'responses': [
                    """📝 **Mid / Internal Marks — Academic Year 2025-26 (Current Semester)**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """| S.No | Code | Subject | CIE-I (10M) | AAT:I-I (5M) | AAT:I-II (5M) | CIE-II (10M) | AAT:II-I (5M) | AAT:II-II (5M) | Total (40M) |\n"""
                    """| 1 | ACSD31 | Theory of Computation | 5 | — | 5 | — | 5 | — | **15** |\n"""
                    """| 2 | ACCD10 | Penetration Testing and Cyber Operations | 5 | — | — | — | — | — | **5** |\n"""
                    """| 3 | ACSD25 | Software Project Management | 8 | — | — | — | — | — | **8** |\n"""
                    """| 4 | ACAD09 | Cyber Physical Systems | 5 | — | 5 | — | — | — | **10** |\n"""
                    """| 5 | AITD18 | Computer Graphics and Multimedia Systems | 4 | — | 5 | — | — | — | **9** |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """📊 **Marks Structure (Total Internal: 40 marks):**\n"""
                    """• **CIE-I (Mid-Term 1):** 10 marks\n"""
                    """• **AAT:I-I:** 5 marks\n"""
                    """• **AAT:I-II:** 5 marks\n"""
                    """• **CIE-II (Mid-Term 2):** 10 marks\n"""
                    """• **AAT:II-I:** 5 marks\n"""
                    """• **AAT:II-II:** 5 marks\n"""
                    """• **Total Internal:** 40 marks\n\n"""
                    """⚠️ **Status:**\n"""
                    """• Theory of Computation — CIE-I + AAT:I-II + AAT:II-I done (15/40)\n"""
                    """• Cyber Physical Systems — CIE-I + AAT:I-II done (10/40)\n"""
                    """• Computer Graphics — CIE-I + AAT:I-II done (9/40)\n"""
                    """• Penetration Testing — Only CIE-I done (5/40)\n"""
                    """• Software Project Management — Only CIE-I done (8/40)\n\n"""
                    """💡 **Note:** '—' indicates marks not yet released.\n"""
                    """📧 For queries, contact your subject faculty."""
                ]
            },
            'library': {
                'patterns': ['library', 'book', 'books', 'reading', 'study material', 'digital library'],
                'responses': [
                    "Library hours: 9:30 AM - 4:00 PM. Access to 50,000+ books, e-journals. Use your student ID to issue books.",
                    "Central library offers study halls, digital library, and research facilities. Maximum 5 books for 15 days."
                ]
            },
            'fee': {
                'patterns': ['fee', 'fees', 'tuition', 'payment', 'cost', 'expense', 'scholarship'],
                'responses': [
                    "Tuition fee: ₹1,01,000/year. Scholarships available based on merit and need.",
                    "Fee structure includes tuition, lab fees, library fees. Payment online via student portal. Contact accounts@iare.ac.in"
                ]
            },
            'event': {
                'patterns': ['event', 'events', 'fest', 'cultural', 'technical', 'sports', 'competition'],
                'responses': [
                    "Upcoming events: Tech fest 'Technozion' in March, Cultural fest 'Spectra' in February. Check notice board for registrations.",
                    "Regular events include workshops, seminars, guest lectures. Follow our social media for latest updates."
                ]
            },
            'faculty': {
                'patterns': ['faculty', 'professor', 'teacher', 'hod', 'department', 'staff', 'teachers', 'faculties', 'show staff', 'list staff', 'all staff', 'all faculty', 'show faculty', 'list faculty', 'college staff', 'college faculty', 'staff members', 'faculty members', 'teaching staff'],
                'responses': []  # Will be dynamically generated with staff list
            },
            'timetable': {
                'patterns': ['timetable', 'schedule', 'class', 'classes', 'timing', 'time table', 'class schedule', 'weekly schedule', 'today classes', 'tomorrow classes', 'period'],
                'responses': [
                    """📅 **CS-VI-SEM-C — Weekly Timetable (23-Mar to 28-Mar-2026)**\n\n"""
                    """**Room: 3206**\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **Monday (23-Mar-2026)**\n"""
                    """| Period | Subject | Faculty ID |\n"""
                    """| I | CPS (CS-VI-SEM-C) | IARE11075 |\n"""
                    """| II | PTCO (CS-VI-SEM-C) | IARE11122 |\n"""
                    """| III | SPM (CS-VI-SEM-C) | IARE11045 |\n"""
                    """| IV | CGMS (CS-VI-SEM-C) | IARE11104 |\n"""
                    """| V | TC (CS-VI-SEM-C) | IARE10999 |\n"""
                    """| VI | PTCO (CS-VI-SEM-C) | IARE11122 |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **Tuesday (24-Mar-2026)**\n"""
                    """| Period | Subject | Faculty ID |\n"""
                    """| I | CPS (CS-VI-SEM-C) | IARE11075 |\n"""
                    """| II | PTCO (CS-VI-SEM-C) | IARE11122 |\n"""
                    """| III | TC (CS-VI-SEM-C) | IARE10999 |\n"""
                    """| IV | DP/DP/DP (CS-VI-SEM-C) — Room: TIIC | IARE11085/IARE11069/IARE11104 |\n"""
                    """| V | DP/DP/DP (CS-VI-SEM-C) — Room: TIIC | IARE11085/IARE11069/IARE11104 |\n"""
                    """| VI | DP/DP/DP (CS-VI-SEM-C) — Room: TIIC | IARE11085/IARE11098/IARE11104 |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **Wednesday (25-Mar-2026)**\n"""
                    """| Period | Subject | Faculty ID |\n"""
                    """| I | CGMS (CS-VI-SEM-C) | IARE11104 |\n"""
                    """| II | SPM (CS-VI-SEM-C) | IARE11045 |\n"""
                    """| III | PTCO (CS-VI-SEM-C) | IARE11122 |\n"""
                    """| IV | CSLL/CSLL/CSLL (CS-VI-SEM-C) — Room: 3307 | IARE10943/IARE11120/IARE11045 |\n"""
                    """| V | CSLL/CSLL/CSLL (CS-VI-SEM-C) — Room: 3307 | IARE10943/IARE11120/IARE11045 |\n"""
                    """| VI | CSLL/CSLL/CSLL (CS-VI-SEM-C) — Room: 3307 | IARE10943/IARE11120/IARE10974 |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **Thursday (26-Mar-2026)**\n"""
                    """| Period | Subject | Faculty ID |\n"""
                    """| I | CPS (CS-VI-SEM-C) | IARE11075 |\n"""
                    """| II | TC (CS-VI-SEM-C) | IARE10999 |\n"""
                    """| III | SPM (CS-VI-SEM-C) | IARE11045 |\n"""
                    """| IV | AIS/AIS/AIS (CS-VI-SEM-C) — Room: 2006 | IARE11118/IARE10974/IARE11120 |\n"""
                    """| V | AIS/AIS/AIS (CS-VI-SEM-C) — Room: 2006 | IARE11118/IARE10974/IARE11056 |\n"""
                    """| VI | AIS/AIS/AIS (CS-VI-SEM-C) — Room: 2006 | IARE11118/IARE10974/IARE11122 |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **Friday (27-Mar-2026)**\n"""
                    """| Period | Subject | Faculty ID |\n"""
                    """| I | PTCL/PTCL/PTCL (CS-VI-SEM-C) | IARE11122/IARE11045/IARE10974 |\n"""
                    """| II | PTCL/PTCL/PTCL (CS-VI-SEM-C) | IARE11122/IARE11045/IARE10974 |\n"""
                    """| III | PTCL/PTCL/PTCL (CS-VI-SEM-C) | IARE11122/IARE11045/IARE10974 |\n"""
                    """| IV | TC (CS-VI-SEM-C) — Room: 3307 | IARE10999 |\n"""
                    """| V | CGMS (CS-VI-SEM-C) — Room: 3307 | IARE11104 |\n"""
                    """| VI | SPORTS (CS-VI-SEM-C) — Room: 3307 | — |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"""
                    """📌 **Saturday (28-Mar-2026)**\n"""
                    """| Period | Subject | Faculty ID |\n"""
                    """| I | CGMS (CS-VI-SEM-C) | IARE11104 |\n"""
                    """| II | SPM (CS-VI-SEM-C) | IARE11045 |\n"""
                    """| III | TC (CS-VI-SEM-C) | IARE10999 |\n"""
                    """| IV | PTCO (CS-VI-SEM-C) | IARE11122 |\n"""
                    """| V | CPS (CS-VI-SEM-C) | IARE11075 |\n"""
                    """| VI | LIBRARY (CS-VI-SEM-C) | IARE11122 |\n\n"""
                    """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
                    """💡 **Note:** All classes are in Room 3206 unless stated otherwise.\n"""
                    """📧 For timetable changes, contact your class coordinator."""
                ]
            },
            'transport': {
                'patterns': ['bus', 'transport', 'transportation', 'route', 'travel', 'shuttle'],
                'responses': [
                    "College buses available from major areas. Route details and timings on transport section of website.",
                    "Bus facility covers 20+ routes. Annual bus fee: ₹15,000. Contact transport office for routes."
                ]
            },
            'wifi': {
                'patterns': ['wifi', 'internet', 'connection', 'network', 'login'],
                'responses': [
                    "WiFi available across campus. Username: Student ID. Contact IT helpdesk for issues.",
                    "WiFi SSIDs: IARE-Student, IARE-Faculty. For connection issues, mail: ithelpdesk@iare.ac.in"
                ]
            },
            'contact': {
                'patterns': ['contact', 'phone', 'email', 'address', 'reach', 'call'],
                'responses': [
                    "Main Office: 040-2345678, Email: info@iare.ac.in, Address: IARE, Dundigal, Hyderabad - 500043",
                    "Admissions: 040-2345679, Accounts: 040-2345680, Principal: principal@iare.ac.in"
                ]
            }
        }
    
    def load_knowledge_base(self):
        """Load FAQs from database"""
        try:
            conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'campus_assistant.db'))
            c = conn.cursor()
            c.execute('SELECT question, answer, keywords FROM faqs')
            knowledge = []
            for row in c.fetchall():
                knowledge.append({
                    'question': row[0],
                    'answer': row[1],
                    'keywords': row[2].split(',') if row[2] else []
                })
            conn.close()
            return knowledge
        except:
            return []
    
    def reload_knowledge_base(self):
        """Reload knowledge base after updates"""
        self.knowledge_base = self.load_knowledge_base()
    
    def preprocess_text(self, text):
        """Clean and normalize input text"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def extract_name_from_message(self, text):
        """Extract person name from the user message, handling departments and titles."""
        # Faculty ID query support
        faculty_id_match = re.search(r"\bIARE\s*(\d{4,})\b", text, flags=re.I)
        if faculty_id_match:
            return f"IARE{faculty_id_match.group(1)}"

        # If message is multiline and includes a clear titled name line, prefer that
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if re.search(r"\b(professor|prof|dr|doctor|mr|ms|mrs|madam|sir)\b", line, flags=re.I):
                line_clean = re.sub(r"\b(professor|prof|dr|doctor|mr|ms|mrs|madam|sir)\b\.?", "", line, flags=re.I)
                line_clean = re.sub(r"[^a-zA-Z\s]", " ", line_clean)
                line_clean = " ".join(w.strip() for w in line_clean.split() if w.strip())
                if 2 <= len(line_clean.split()) <= 5:
                    return line_clean.strip()

        # Remove common query phrases
        t = re.sub(r"(tell me about|about|info on|information|details|who is|what is|profile of|show me|info|profile)", "", text, flags=re.I)
        
        # Remove titles
        t = re.sub(r"\b(professor|prof|dr|doctor|mr|ms|mrs|madam|sir)\b\.?", "", t, flags=re.I)
        
        # Remove department references (CSE, ECE, EEE, MECH, etc.) and variations
        t = re.sub(r"\b(cse|ece|eee|mech|civil|it|mechanical|electrical|electronics|computer science|cs|ec)\b", "", t, flags=re.I)
        t = re.sub(r"\(.*?\)", "", t)  # Remove anything in parentheses like (cs), (cse)
        t = re.sub(r"\bof\b", "", t, flags=re.I)  # Remove "of" preposition
        
        # Remove common stop words
        t = re.sub(r"\b(the|is|at|in|for|on|from|about|department|dept|faculty|staff)\b", "", t, flags=re.I)

        # Remove profile field labels frequently present in copied faculty details
        t = re.sub(r"\b(faculty id|designation|total experience|experience at iare|date of birth|email id|employment status|jntuh id|aicte faculty id|undergraduate degree|postgraduate degree|ph\.?d degree|areas of specialization|academic identity|video lectures|youtube link|vidwan link)\b", "", t, flags=re.I)
        
        # Clean up extra spaces and trim
        name = " ".join([w.strip() for w in t.split() if w.strip()])
        return name.strip()

    def fetch_all_staff(self):
        """Fetch list of all staff/faculty from iare.ac.in website.
        
        Returns a list of staff members with their basic info.
        """
        now_ts = datetime.now().timestamp()
        if self._staff_cache and (now_ts - self._staff_cache_time) < self._staff_cache_ttl:
            return self._staff_cache
        base = "https://www.iare.ac.in"
        staff_list = []
        
        try:
            # Try to find faculty/staff pages
            resp = requests.get(base, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Collect faculty/staff page links
            faculty_urls = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/'):
                    full = base + href
                elif href.startswith('http'):
                    full = href
                else:
                    continue
                
                # Look for faculty, staff, or department pages
                if any(keyword in href.lower() for keyword in ['faculty', 'staff', 'people', 'department', 'team']):
                    faculty_urls.add(full)
            
            # Scan each faculty page for staff information
            for url in list(faculty_urls)[:15]:  # Increased to 15 pages for better coverage
                try:
                    page_resp = requests.get(url, timeout=8)
                    if page_resp.status_code != 200:
                        continue
                    
                    page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                    
                    # Strategy 1: Look for staff cards with class patterns
                    for elem in page_soup.find_all(['div', 'section', 'article'], class_=lambda x: x and any(k in str(x).lower() for k in ['faculty', 'staff', 'profile', 'member', 'team', 'card'])):
                        name_tag = elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b', 'a'])
                        if not name_tag:
                            continue
                        
                        name = name_tag.get_text(strip=True)
                        
                        # Skip if name is too short or contains common non-name text
                        if len(name) < 3 or any(skip in name.lower() for skip in ['department', 'faculty list', 'staff list', 'contact us', 'about']):
                            continue
                        
                        text_content = elem.get_text(separator=' ')
                        
                        # Extract designation
                        designation = ''
                        des_match = re.search(r'(Professor|Assistant Professor|Associate Professor|Head of Department|HOD|Lecturer|Faculty|Dean|Director|Asst\.\s*Professor|Assoc\.\s*Professor)', text_content, re.I)
                        if des_match:
                            designation = des_match.group(0)
                        
                        # Extract email
                        email = ''
                        email_link = elem.find('a', href=lambda h: h and h.startswith('mailto:'))
                        if email_link:
                            email = email_link['href'].split(':', 1)[1].split('?')[0]
                        else:
                            email_match = re.search(r'[\w\.\-]+@[\w\.-]+\.[a-zA-Z]{2,6}', text_content)
                            if email_match:
                                email = email_match.group(0)
                        
                        # Extract phone
                        phone = ''
                        tel_link = elem.find('a', href=lambda h: h and h.startswith('tel:'))
                        if tel_link:
                            phone = tel_link['href'].split(':', 1)[1]
                        else:
                            phone_match = re.search(r'(?:\+91[\s-]?)?(?:\d{10}|\d{3}[\s-]\d{3}[\s-]\d{4})', text_content)
                            if phone_match:
                                phone = phone_match.group(0)
                        
                        # Only add if we have at least name and one other detail
                        if name and (designation or email):
                            staff_member = {
                                'name': name,
                                'designation': designation,
                                'email': email,
                                'phone': phone,
                                'profile_url': url
                            }
                            
                            # Avoid duplicates
                            if not any(s['name'].lower() == name.lower() for s in staff_list):
                                staff_list.append(staff_member)
                    
                    # Strategy 2: Look for tables with faculty information
                    for table in page_soup.find_all('table'):
                        rows = table.find_all('tr')
                        for row in rows[1:]:  # Skip header row
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                name = cells[0].get_text(strip=True)
                                if len(name) >= 3 and not any(skip in name.lower() for skip in ['name', 'faculty', 'sr', 'no', 's.no']):
                                    email = ''
                                    designation = ''
                                    for cell in cells[1:]:
                                        cell_text = cell.get_text(strip=True)
                                        if '@' in cell_text:
                                            email = cell_text
                                        elif any(title in cell_text.lower() for title in ['professor', 'lecturer', 'hod', 'dean']):
                                            designation = cell_text
                                    
                                    if name and (designation or email):
                                        staff_member = {
                                            'name': name,
                                            'designation': designation,
                                            'email': email,
                                            'phone': '',
                                            'profile_url': url
                                        }
                                        if not any(s['name'].lower() == name.lower() for s in staff_list):
                                            staff_list.append(staff_member)
                
                except Exception as e:
                    continue
            
            # Merge with fallback data
            # Add fallback staff that aren't already in the scraped list
            for fallback_staff in self.fallback_staff_data:
                if not any(s['name'].lower() == fallback_staff['name'].lower() for s in staff_list):
                    staff_list.append(fallback_staff)
            
            # Return merged list (always has at least fallback data)
            self._staff_cache = staff_list
            self._staff_cache_time = now_ts
            return self._staff_cache
            
        except Exception as e:
            # Return fallback data on error
            return self.fallback_staff_data

    def fetch_staff_profile(self, name):
        """Attempt to find staff profile on iare.ac.in and extract contact details.

        Strategy:
        - First check if we can find them in the full staff list (faster)
        - Then fetch homepage and collect candidate links that look like faculty/staff/profile pages
        - Visit each candidate and look for the provided name tokens
        - Extract name, designation, email, phone and profile URL when found
        - Handle partial name matches (e.g., "ramadevi" matches "Dr. Ramadevi G")
        """
        if not name or len(name) < 2:
            return None

        # First try to find in the full staff list (faster and more reliable)
        try:
            staff_list = self.fetch_all_staff()
            if staff_list and len(staff_list) > 0:  # Check if list is not empty
                name_lower = name.lower()
                faculty_id_match = re.search(r"\biare\s*(\d{4,})\b", name_lower)
                normalized_faculty_id = f"iare{faculty_id_match.group(1)}" if faculty_id_match else None

                raw_tokens = re.findall(r"[a-z0-9]+", name_lower)
                ignore_tokens = {
                    'faculty', 'staff', 'information', 'details', 'detail', 'designation', 'department',
                    'experience', 'date', 'birth', 'email', 'employment', 'status', 'jntuh', 'aicte',
                    'undergraduate', 'postgraduate', 'degree', 'specialization', 'academic', 'identity',
                    'video', 'lectures', 'youtube', 'link', 'vidwan', 'full', 'time', 'years', 'months',
                    'assistant', 'associate', 'professor', 'doctor', 'dr', 'mr', 'ms', 'mrs', 'madam', 'sir'
                }
                name_tokens = [
                    token for token in raw_tokens
                    if token not in ignore_tokens and (len(token) > 1 or re.fullmatch(r"[a-z]", token))
                ]

                # Faculty ID direct match
                if normalized_faculty_id:
                    for staff in staff_list:
                        staff_faculty_id = (staff.get('faculty_id') or '').replace(' ', '').lower()
                        if staff_faculty_id == normalized_faculty_id:
                            return staff

                best_staff = None
                best_score = 0
                
                # Look for matches
                for staff in staff_list:
                    staff_name_lower = staff['name'].lower()
                    staff_name_tokens = re.findall(r"[a-z]+", staff_name_lower)
                    
                    # Exact match
                    if name_lower in staff_name_lower:
                        return staff

                    # Token-overlap scoring to support initials + full name combinations
                    score = 0
                    for token in name_tokens:
                        if token in staff_name_tokens:
                            score += 2 if len(token) >= 3 else 1
                        elif len(token) >= 3 and any(part.startswith(token) or token in part for part in staff_name_tokens):
                            score += 1

                    if score > best_score:
                        best_score = score
                        best_staff = staff

                # Return best deterministic match when score is strong enough
                if best_staff and best_score >= 4:
                    return best_staff
        except Exception as e:
            print(f"Staff list lookup failed: {e}")  # Debug logging
            pass  # Continue with web scraping if staff list fails

        base = "https://www.iare.ac.in"
        try:
            resp = requests.get(base, timeout=8)
            resp.raise_for_status()
        except Exception:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        links = set()
        # gather candidate links from homepage
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                full = base + href
            elif href.startswith('http'):
                full = href
            else:
                continue

            if any(k in href.lower() for k in ['faculty', 'staff', 'profile', 'people', 'department', 'cse', 'ece', 'eee']):
                links.add(full)

        # always include homepage as fallback
        links.add(base)

        name_tokens = [t.lower() for t in name.split() if len(t) > 1]

        for url in links:
            try:
                r = requests.get(url, timeout=8)
                if r.status_code != 200:
                    continue
                page = BeautifulSoup(r.text, 'html.parser')
                page_text = page.get_text(separator=' ').lower()

                # More flexible check: at least one substantial token must appear
                if not any(tok in page_text for tok in name_tokens if len(tok) >= 3):
                    continue

                # try to find a heading or element that contains the name
                candidate = None
                best_match_score = 0
                
                for tag in page.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'div', 'p', 'span', 'strong']):
                    t = tag.get_text(separator=' ').strip().lower()
                    
                    # Count how many tokens match
                    match_count = sum(1 for tok in name_tokens if tok in t)
                    
                    # Check if this is a better match
                    if match_count > best_match_score and match_count > 0:
                        # Make sure it's likely a person's name (not too long, contains letters)
                        if len(t.split()) <= 6 and re.search(r'[a-z]', t):
                            best_match_score = match_count
                            candidate = tag

                # build profile object
                profile_name = ' '.join([w.capitalize() for w in name.split()])
                designation = ''
                email = ''
                phone = ''

                if candidate:
                    # Use the actual name found on the page
                    actual_name = candidate.get_text(separator=' ').strip()
                    if actual_name and len(actual_name.split()) <= 6:
                        profile_name = actual_name
                    
                    parent = candidate.parent
                    # Also check grandparent for more context
                    if parent and parent.parent:
                        block_text = parent.parent.get_text(separator=' ')
                    else:
                        block_text = parent.get_text(separator=' ') if parent else ''
                    
                    # email
                    m_email = re.search(r'[\w\.\-]+@[\w\.-]+\.[a-zA-Z]{2,6}', block_text)
                    if m_email:
                        email = m_email.group(0)
                    # phone-like patterns
                    m_phone = re.search(r'(?:\+?\d{1,3}[\s-]?)?(?:\d{2,4}[\s-])?\d{6,12}', block_text)
                    if m_phone:
                        phone = m_phone.group(0)
                    # designation heuristics
                    m_des = re.search(r'(Professor|Assistant Professor|Associate Professor|Head of Department|HOD|Lecturer|Faculty)', block_text, re.I)
                    if m_des:
                        designation = m_des.group(0)

                # fallback: find mailto and tel links near the name
                if not email:
                    a_mail = page.find('a', href=lambda h: h and h.startswith('mailto:'))
                    if a_mail:
                        email = a_mail['href'].split(':', 1)[1].split('?')[0]
                if not phone:
                    a_tel = page.find('a', href=lambda h: h and h.startswith('tel:'))
                    if a_tel:
                        phone = a_tel['href'].split(':', 1)[1]

                profile = {
                    'name': profile_name,
                    'designation': designation,
                    'email': email,
                    'phone': phone,
                    'profile_url': url
                }

                # At least return email or designation to consider it a match
                if profile['email'] or profile['designation']:
                    return profile

            except Exception:
                continue

        return None
    
    def get_student_marks(self, user_id='23951A62B0'):
        """Retrieve and format student marks from database"""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT subject_code, subject_name, assignment1, assignment2, 
                       quiz1, quiz2, mid1, mid2, total
                FROM student_marks
                WHERE user_id = ?
                ORDER BY subject_code
            ''', (user_id,))
            
            marks = cursor.fetchall()
            conn.close()
            
            if not marks:
                return "No marks data available. Please check with your faculty or admin."
            
            # Format the response
            response = "📊 **Your Academic Performance:**\n\n"
            
            for idx, mark in enumerate(marks, 1):
                subject_code, subject_name, a1, a2, q1, q2, m1, m2, total = mark
                
                response += f"**{idx}. {subject_name}** ({subject_code})\n"
                response += f"   • Assignment 1: {a1} | Assignment 2: {a2}\n"
                response += f"   • Quiz 1: {q1} | Quiz 2: {q2}\n"
                response += f"   • Mid-1: {m1} | Mid-2: {m2}\n"
                response += f"   • **Total Internal: {total}/40**\n\n"
            
            response += "\n📌 **Note:** End semester exam (60 marks) will be added after semester completion."
            
            return response
            
        except Exception as e:
            print(f"Error fetching marks: {e}")
            return "Unable to retrieve marks at this time. Please contact the admin office."
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def detect_intent(self, user_message):
        """Detect user intent from message"""
        preprocessed = self.preprocess_text(user_message)
        
        # Special handling for person-related queries
        # Check if asking about a person (faculty/staff)
        person_query_patterns = [
            r'\bwho\s+is\b',
            r'\btell\s+me\s+about\b',
            r'\binfo\s+about\b',
            r'\bprofile\s+of\b',
            r'\bdetails\s+of\b'
        ]
        has_person_query = any(re.search(pattern, user_message, re.I) for pattern in person_query_patterns)
        
        # Check for titles or department mentions (indicates person query)
        has_title = re.search(r'\b(prof|professor|dr|doctor|mr|ms|mrs|madam|sir)\b', user_message, re.I)
        has_department = re.search(r'\b(cse|ece|eee|mech|civil|it|cs|ec|department|dept)\b', user_message, re.I)
        has_faculty_reference = re.search(r'\b(faculty|staff|professor|prof|teacher|hod|assistant professor|associate professor)\b', user_message, re.I)
        has_faculty_id = re.search(r'\bIARE\s*\d{4,}\b', user_message, re.I)

        profile_keyword_matches = re.findall(
            r'\b(designation|department|total\s+experience|experience\s+at\s+iare|date\s+of\s+birth|email\s*id|employment\s+status|jntuh\s+id|aicte\s+faculty\s+id|undergraduate\s+degree|postgraduate\s+degree|ph\.?d\s+degree|areas\s+of\s+specialization|academic\s+identity|video\s+lectures|vidwan|youtube)\b',
            user_message,
            re.I
        )
        has_profile_text_block = len(profile_keyword_matches) >= 2
        
        # If it's a person query or department-level faculty query, force faculty intent
        if has_person_query or (has_title and has_department) or has_faculty_id or (has_faculty_reference and (has_title or has_profile_text_block)) or (has_faculty_reference and has_department):
            return 'faculty', 0.85
        
        # Force timetable intent for schedule/timing/class queries (prevent knowledge base override)
        timetable_keywords = re.search(r'\b(timetable|time\s*table|class\s*schedule|weekly\s*schedule|today\s*classes|tomorrow\s*classes|class\s*timing|college\s*timing|period|my\s*schedule|my\s*classes|show\s*schedule)\b', user_message, re.I)
        if timetable_keywords:
            return 'timetable', 0.90
        
        # Force internal_marks intent for mid/internal/cia queries (prevent knowledge base override)
        mid_keywords = re.search(r'\b(mid\s*marks|internal\s*marks|cia\s*marks|mid\s*term|cie\s*marks|cie|cia|mid\s*1|mid\s*2|aat\s*marks|internal|internals|mid\s*exam|current\s*marks|mid)\b', user_message, re.I)
        if mid_keywords:
            return 'internal_marks', 0.90
        
        best_match = None
        best_score = 0.0
        
        # Check against intent patterns
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data['patterns']:
                if pattern in preprocessed:
                    score = len(pattern) / len(preprocessed) if preprocessed else 0
                    if score > best_score:
                        best_score = score
                        best_match = intent_name
        
        # Check against knowledge base
        for kb_item in self.knowledge_base:
            similarity = self.calculate_similarity(
                preprocessed,
                self.preprocess_text(kb_item['question'])
            )
            
            # Check keywords
            for keyword in kb_item['keywords']:
                if keyword.lower() in preprocessed:
                    similarity += 0.2
            
            if similarity > best_score and similarity > 0.5:
                best_score = similarity
                best_match = 'knowledge_base'
        
        confidence = min(best_score * 1.5, 1.0)
        
        return best_match, confidence
    
    def get_response(self, user_message, user_id=None):
        """Generate response for user message"""
        intent, confidence = self.detect_intent(user_message)
        
        response = ""
        suggestions = []
        
        # Handle None intent or very low confidence
        if not intent or confidence < 0.3:
            # Low confidence - provide default response
            response = "I'm not sure I understood that correctly. Could you please rephrase? You can ask me about:\n\n"
            response += "• Admissions & Applications\n• Placements & Careers\n• Hostel & Accommodation\n"
            response += "• Exams & Results\n• Library & Resources\n• Events & Activities\n• Fees & Scholarships\n"
            response += "• Faculty & Staff Information"
            
            suggestions = ['Admission process', 'Placement statistics', 'Show all staff', 'Library hours']
        
        elif intent == 'knowledge_base':
            # Match from knowledge base
            preprocessed = self.preprocess_text(user_message)
            best_match = None
            best_similarity = 0
            
            for kb_item in self.knowledge_base:
                similarity = self.calculate_similarity(
                    preprocessed,
                    self.preprocess_text(kb_item['question'])
                )
                
                for keyword in kb_item['keywords']:
                    if keyword.lower() in preprocessed:
                        similarity += 0.2
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = kb_item
            
            if best_match:
                response = best_match['answer']
            else:
                response = "I found some information but I'm not entirely sure. Please contact the administrative office for accurate information."
        
        else:
            # Intent matched - get response
            # Special handling for faculty intent
            if intent == 'faculty':
                # Check if user is asking about a specific person
                person_title_re = re.search(r"\b(prof|professor|dr|doctor|mr|ms|mrs|madam|sir)\b", user_message, re.I)
                who_is_pattern = re.search(r"\b(who is|tell me about|info about|details of|profile of)\b", user_message, re.I)
                name_guess = self.extract_name_from_message(user_message)
                
                # Determine if this is a specific person query
                is_specific_person = False
                if name_guess and len(name_guess) >= 3:  # At least 3 chars for a name
                    # It's specific if:
                    # 1. Has a title (Prof, Dr, etc.)
                    # 2. Has "who is" or similar pattern
                    # 3. Name has at least one word that's not too generic
                    name_words = name_guess.split()
                    has_substantial_name = any(len(w) >= 4 for w in name_words)
                    
                    if person_title_re or who_is_pattern or has_substantial_name:
                        is_specific_person = True
                
                # If specific name mentioned, fetch individual profile
                if is_specific_person:
                    profile = self.fetch_staff_profile(name_guess)
                    if profile:
                        response = f"👤 **{profile['name']}**\n\n"
                        
                        # Basic Information
                        if profile.get('faculty_id'):
                            response += f"**Faculty ID:** {profile['faculty_id']}\n\n"
                        
                        if profile.get('designation'):
                            response += f"**Designation:** {profile['designation']}\n\n"
                        
                        if profile.get('department'):
                            response += f"**Department:** {profile['department']}\n\n"
                        
                        # Contact Details
                        if profile.get('email'):
                            response += f"**Email ID:** {profile['email']}\n\n"
                        
                        if profile.get('phone') and profile['phone']:
                            response += f"**Phone:** {profile['phone']}\n\n"
                        
                        # Experience
                        if profile.get('experience'):
                            response += f"**Total Experience:** {profile['experience']}\n\n"
                        
                        if profile.get('experience_iare'):
                            response += f"**Experience at IARE:** {profile['experience_iare']}\n\n"
                        
                        if profile.get('employment_status'):
                            response += f"**Employment Status:** {profile['employment_status']}\n\n"
                        
                        # Personal Details
                        if profile.get('dob'):
                            response += f"**Date of Birth:** {profile['dob']}\n\n"
                        
                        # Academic IDs
                        if profile.get('jntuh_id'):
                            response += f"**JNTUH ID:** {profile['jntuh_id']}\n\n"
                        
                        if profile.get('aicte_id'):
                            response += f"**AICTE Faculty ID:** {profile['aicte_id']}\n\n"
                        
                        # Educational Qualifications
                        if profile.get('ug_degree'):
                            response += f"**Undergraduate Degree:** {profile['ug_degree']}\n\n"
                        
                        if profile.get('pg_degree'):
                            response += f"**Postgraduate Degree:** {profile['pg_degree']}\n\n"
                        
                        if profile.get('phd_degree'):
                            response += f"**Ph.D Degree:** {profile['phd_degree']}\n\n"
                        
                        if profile.get('qualification') and not profile.get('phd_degree'):
                            response += f"**Qualification:** {profile['qualification']}\n\n"
                        
                        # Specialization
                        if profile.get('specialization'):
                            response += f"**Areas of Specialization:** {profile['specialization']}\n\n"
                        
                        # Links
                        if profile.get('vidwan_link'):
                            response += f"**Academic Identity:** [View Vidwan Profile]({profile['vidwan_link']})\n\n"
                        
                        if profile.get('youtube_link'):
                            response += f"**Video Lectures:** [YouTube Channel]({profile['youtube_link']})\n\n"
                        
                        if profile.get('profile_url'):
                            response += f"**Profile Page:** [Click here to view]({profile['profile_url']})\n\n"
                        
                        suggestions = ['Show all staff', 'Department contacts', 'More faculty info']
                        intent = 'faculty_profile'
                        confidence = 0.95
                        return {
                            'response': response.strip(),
                            'intent': intent,
                            'confidence': round(confidence, 2),
                            'suggestions': suggestions
                        }
                    else:
                        # Name extraction worked but profile not found
                        response = f"I couldn't find detailed information about '{name_guess}' in the faculty directory. This could be because:\n\n"
                        response += "• The name spelling might be different\n"
                        response += "• They might not have a public profile page\n"
                        response += "• The information isn't available on the website\n\n"
                        response += "💡 **Try:**\n"
                        response += "• Using their full name\n"
                        response += "• Checking the full staff list (type 'show all staff')\n"
                        response += "• Contacting the department office directly"
                        suggestions = ['Show all staff', 'Department contacts']
                        return {
                            'response': response,
                            'intent': 'faculty_not_found',
                            'confidence': 0.8,
                            'suggestions': suggestions
                        }
                
                # Check if user is asking about a specific department
                dept_map = {
                    'cse': ['CSE', 'Computer Science', 'CSE Cyber Security', 'CSE Data Science', 'CSE-AIML', 'CSE-DS'],
                    'computer science': ['CSE', 'Computer Science', 'CSE Cyber Security', 'CSE Data Science', 'CSE-AIML', 'CSE-DS'],
                    'cyber security': ['CSE Cyber Security'],
                    'cs': ['CSE', 'Computer Science', 'CSE Cyber Security', 'CSE Data Science', 'CSE-AIML', 'CSE-DS'],
                    'aiml': ['CSE-AIML'],
                    'ai ml': ['CSE-AIML'],
                    'artificial intelligence': ['CSE-AIML'],
                    'machine learning': ['CSE-AIML'],
                    'data science': ['CSE-DS', 'CSE Data Science'],
                    'ds': ['CSE-DS', 'CSE Data Science'],
                    'ece': ['ECE'],
                    'electronics': ['ECE'],
                    'eee': ['EEE'],
                    'electrical': ['EEE'],
                    'mech': ['MECH'],
                    'mechanical': ['MECH'],
                    'civil': ['CIVIL'],
                    'it': ['IT'],
                    'information technology': ['IT'],
                    'aero': ['AERO'],
                    'aeronautical': ['AERO'],
                    'mba': ['MBA'],
                    'sh': ['S&H'],
                    'science': ['S&H'],
                    'humanities': ['S&H'],
                    'administration': ['Administration'],
                }
                
                msg_lower = user_message.lower()
                matched_departments = None
                matched_dept_name = None
                
                for key, dept_names in dept_map.items():
                    if re.search(r'\b' + re.escape(key) + r'\b', msg_lower):
                        matched_departments = dept_names
                        matched_dept_name = key.upper()
                        break
                
                staff_list = self.fetch_all_staff()
                print(f"Staff list fetched: {len(staff_list) if staff_list else 0} members")
                
                if matched_departments and staff_list:
                    # Filter faculty by the matched department
                    dept_faculty = [s for s in staff_list if s.get('department', '') in matched_departments]
                    
                    if dept_faculty:
                        response = f"👥 **{matched_dept_name} Department — Faculty List**\n\n"
                        for i, staff in enumerate(dept_faculty, 1):
                            response += f"**{i}. {staff['name']}**\n"
                            if staff.get('faculty_id'):
                                response += f"   • **Faculty ID:** {staff['faculty_id']}\n"
                            if staff.get('designation'):
                                response += f"   • **Designation:** {staff['designation']}\n"
                            if staff.get('department'):
                                response += f"   • **Department:** {staff['department']}\n"
                            if staff.get('email'):
                                response += f"   • **Email:** {staff['email']}\n"
                            if staff.get('phone') and staff['phone']:
                                response += f"   • **Phone:** {staff['phone']}\n"
                            if staff.get('qualification'):
                                response += f"   • **Qualification:** {staff['qualification']}\n"
                            if staff.get('specialization'):
                                response += f"   • **Specialization:** {staff['specialization']}\n"
                            if staff.get('experience'):
                                response += f"   • **Experience:** {staff['experience']}\n"
                            if staff.get('profile_url'):
                                response += f"   • **Profile:** [View Profile]({staff['profile_url']})\n"
                            response += "\n"
                        
                        response += f"\n**Total {matched_dept_name} Faculty:** {len(dept_faculty)}\n"
                        response += f"\n💡 **Tip:** For detailed info about a specific faculty member, ask:\n• \"Tell me about Prof. [Name]\"\n• \"Who is Dr. [Name]?\""
                        suggestions = ['Show all departments', 'CSE faculty', 'ECE faculty', 'HOD info']
                        confidence = 0.95
                        return {
                            'response': response,
                            'intent': 'faculty_department',
                            'confidence': round(confidence, 2),
                            'suggestions': suggestions
                        }
                    else:
                        response = f"No faculty data found for the **{matched_dept_name}** department at this time.\n\n"
                        response += "💡 Try asking about another department or type **\"faculty\"** to see all departments."
                        suggestions = ['Show all departments', 'CSE faculty', 'ECE faculty']
                        return {
                            'response': response,
                            'intent': 'faculty_department',
                            'confidence': 0.8,
                            'suggestions': suggestions
                        }
                
                elif staff_list and len(staff_list) > 0:
                    # No specific department — show department directory
                    departments = {}
                    for staff in staff_list:
                        dept = staff.get('department', 'Other')
                        if dept not in departments:
                            departments[dept] = []
                        departments[dept].append(staff['name'])
                    
                    response = "🏛️ **IARE — Department & Faculty Directory**\n\n"
                    response += "Here are the departments available. Ask about any department to see its faculty details.\n\n"
                    
                    dept_number = 1
                    for dept, members in departments.items():
                        # Find HOD if available
                        hod_name = None
                        for staff in staff_list:
                            if staff.get('department') == dept and 'HOD' in staff.get('designation', '').upper():
                                hod_name = staff['name']
                                break
                            if staff.get('department') == dept and 'Head' in staff.get('designation', ''):
                                hod_name = staff['name']
                                break
                        
                        response += f"**{dept_number}. {dept}**\n"
                        response += f"   • Faculty Members: {len(members)}\n"
                        if hod_name:
                            response += f"   • HOD/Head: {hod_name}\n"
                        response += "\n"
                        dept_number += 1
                    
                    response += f"\n**Total Departments:** {len(departments)} | **Total Faculty:** {len(staff_list)}\n\n"
                    response += "💡 **To view faculty of a department, ask like:**\n"
                    response += "• \"CSE faculty\"\n"
                    response += "• \"Show ECE staff\"\n"
                    response += "• \"MECH department faculty\"\n"
                    response += "• \"Who is Dr. [Name]?\""
                    suggestions = ['CSE faculty', 'ECE faculty', 'EEE faculty', 'MECH faculty']
                    confidence = 0.95
                    return {
                        'response': response,
                        'intent': 'faculty_departments',
                        'confidence': round(confidence, 2),
                        'suggestions': suggestions
                    }
                else:
                    # Fallback if scraping fails or returns empty
                    response = "I'm currently unable to fetch the faculty list. This might be due to:\n\n"
                    response += "• Network connectivity issues\n"
                    response += "• Temporary server unavailability\n\n"
                    response += "**Please try:**\n"
                    response += "• Asking about a specific department (e.g., 'CSE faculty')\n"
                    response += "• Visiting https://www.iare.ac.in/departments directly\n\n"
                    response += "**Contact:** 📧 info@iare.ac.in | 📞 040-2345678"
                    suggestions = ['Try again', 'CSE faculty', 'ECE faculty']
            
            elif intent == 'marks':
                # Handle marks/grades/results request
                responses = self.intents[intent]['responses']
                response = random.choice(responses) if responses else self.get_student_marks(user_id=user_id or '23951A62B0')
                suggestions = ['Exam schedule', 'Attendance', 'Timetable']
            
            elif intent in self.intents:
                responses = self.intents[intent]['responses']
                response = random.choice(responses)
                
                # Add related suggestions
                related_intents = [k for k in self.intents.keys() if k != intent][:3]
                suggestions = [self.intents[k]['patterns'][0].title() + ' info' for k in related_intents]
        
        return {
            'response': response,
            'intent': intent if intent else 'unknown',
            'confidence': round(confidence, 2),
            'suggestions': suggestions
        }

# Initialize some default FAQs
def init_default_faqs():
    """Initialize database with default FAQs"""
    default_faqs = [
        # ── General ──
        {
            'category': 'General',
            'question': 'What is the college timing?',
            'answer': 'College timings are from 9:00 AM to 4:30 PM on regular days. Labs may extend till 5:30 PM.',
            'keywords': 'timing,hours,schedule,time'
        },
        {
            'category': 'General',
            'question': 'Where is IARE located?',
            'answer': 'IARE (Institute of Aeronautical Engineering) is located at Dundigal, Hyderabad, Telangana - 500043. It is about 30 km from Secunderabad Railway Station and 20 km from Rajiv Gandhi International Airport.',
            'keywords': 'location,address,where,campus,dundigal'
        },
        {
            'category': 'General',
            'question': 'What are the college holidays?',
            'answer': 'IARE follows the academic calendar published by JNTUH. Major holidays include Dussehra (Oct), Diwali (Oct/Nov), Sankranti (Jan), and summer vacation (May-Jun). The complete holiday list is published at the start of each academic year.',
            'keywords': 'holidays,vacation,leave,break,off'
        },
        {
            'category': 'General',
            'question': 'What is the dress code at IARE?',
            'answer': 'Students must wear the prescribed college uniform on all working days. Boys: IARE grey trousers, white shirt with college logo. Girls: IARE churidar with dupatta. ID card must be worn visibly at all times.',
            'keywords': 'dress,code,uniform,clothing,attire'
        },
        {
            'category': 'General',
            'question': 'What is the anti-ragging policy?',
            'answer': 'IARE has a zero-tolerance policy against ragging. An Anti-Ragging Committee and Squad are active on campus. Students must submit online anti-ragging affidavits on admission. Complaints can be reported to the committee or via the UGC helpline: 1800-180-5522.',
            'keywords': 'ragging,anti,policy,complaint,safety'
        },
        {
            'category': 'General',
            'question': 'How do I get a bonafide certificate?',
            'answer': 'Apply for a bonafide certificate at the Administrative Office with your ID card. Processing takes 2-3 working days. You can also request it online through the student portal under "Certificates" section.',
            'keywords': 'bonafide,certificate,letter,document'
        },

        # ── Admissions ──
        {
            'category': 'Admissions',
            'question': 'What are the eligibility criteria for B.Tech admission?',
            'answer': 'For B.Tech: Minimum 60% in 10+2 with Physics, Chemistry, and Mathematics. Valid entrance exam score (TG EAMCET / AP EAMCET / JEE Main) required. Admission through TSCHE counselling or management quota.',
            'keywords': 'eligibility,btech,requirements,criteria'
        },
        {
            'category': 'Admissions',
            'question': 'What courses does IARE offer?',
            'answer': 'IARE offers: B.Tech in CSE, CSE (AI&ML), CSE (Data Science), CSE (Cyber Security), ECE, EEE, ME, CE, Aeronautical Engineering, and IT. Post-graduate: M.Tech in various specializations and MBA. Ph.D programs also available.',
            'keywords': 'courses,programs,branches,departments,btech,mtech,mba'
        },
        {
            'category': 'Admissions',
            'question': 'How to apply for admission at IARE?',
            'answer': '1) Register on the TSCHE/APSCHE counselling portal.\n2) Attend EAMCET/JEE counselling and select IARE.\n3) Report to college with allotment order, original certificates, and fee receipt.\n4) For management quota, apply directly at admissions.iare.ac.in or contact 040-24680600.',
            'keywords': 'apply,admission,process,join,enroll,register'
        },
        {
            'category': 'Admissions',
            'question': 'What documents are required for admission?',
            'answer': 'Required documents:\n• 10th & 12th mark sheets and certificates (originals + 2 copies)\n• Transfer Certificate (TC)\n• Migration Certificate\n• Allotment Order (if through counselling)\n• Aadhar Card\n• Caste & Income certificates (if applicable)\n• 4 passport-size photographs\n• EAMCET / JEE scorecard\n• Parent/Guardian ID proof',
            'keywords': 'documents,certificates,papers,required,admission'
        },
        {
            'category': 'Admissions',
            'question': 'Is there lateral entry admission?',
            'answer': 'Yes, IARE offers lateral entry into 2nd year B.Tech for diploma holders and B.Sc graduates. Admission is through TS ECET counselling. Eligible branches: CSE, ECE, EEE, ME, CE.',
            'keywords': 'lateral,entry,diploma,ecet,second,year'
        },

        # ── Placements ──
        {
            'category': 'Placements',
            'question': 'What are the placement statistics at IARE?',
            'answer': 'IARE placement highlights:\n• 85%+ placement rate\n• 200+ recruiting companies\n• Highest package: ₹44 LPA\n• Average package: ₹6.5 LPA\n• Top recruiters: TCS, Infosys, Wipro, Amazon, Microsoft, Google, Accenture, Cognizant, Capgemini, HCL, Tech Mahindra, DXC Technology.',
            'keywords': 'placement,statistics,package,salary,company,recruiters'
        },
        {
            'category': 'Placements',
            'question': 'When do placements start?',
            'answer': 'Campus placements typically begin in July/August for final-year students. Pre-placement training starts from 3rd year (6th semester). The Training & Placement cell conducts mock interviews, aptitude tests, and soft skills training throughout the year.',
            'keywords': 'placement,start,when,begin,training,schedule'
        },
        {
            'category': 'Placements',
            'question': 'How to register for placements?',
            'answer': 'Register for placements through the Placement Portal:\n1) Login to the student portal.\n2) Update your resume and profile.\n3) Register for eligible drives.\n4) Attend pre-placement talk.\n5) Clear aptitude test, technical round, and HR interview.\nContact: placements@iare.ac.in',
            'keywords': 'register,placement,portal,apply,drive'
        },
        {
            'category': 'Placements',
            'question': 'What is the placement training provided?',
            'answer': 'IARE provides comprehensive placement training:\n• Aptitude & Reasoning (Quantitative, Logical, Verbal)\n• Programming (C, Java, Python, DSA)\n• Soft Skills & Communication\n• Group Discussion Practice\n• Mock Interviews with industry experts\n• Resume Building Workshops\n• Company-specific preparation\nTraining is conducted by both internal faculty and external trainers.',
            'keywords': 'training,placement,aptitude,skills,preparation'
        },
        {
            'category': 'Placements',
            'question': 'What internship opportunities are available?',
            'answer': 'IARE facilitates internships through:\n• Industry tie-ups with 100+ companies\n• Summer internships (May-June) for 2nd & 3rd year students\n• Semester-long internships in final year\n• AICTE internship portal\n• Virtual internships available year-round\nContact the T&P cell for current openings.',
            'keywords': 'internship,intern,summer,industry,opportunity'
        },

        # ── Academics / Exams ──
        {
            'category': 'Academics',
            'question': 'How many credits are required for graduation?',
            'answer': 'Total 160 credits required for B.Tech graduation. This includes core courses (100 credits), electives (24 credits), lab work (20 credits), project/internship (12 credits), and mandatory courses (4 credits).',
            'keywords': 'credits,graduation,degree,requirements'
        },
        {
            'category': 'Academics',
            'question': 'What is the exam pattern at IARE?',
            'answer': 'IARE examination pattern per subject:\n• CIA-1 (Mid-Term 1): 10 marks\n• CIA-2 (Mid-Term 2): 10 marks\n• AAT (Quiz/Assignment/Presentation): 5 marks\n• Attendance: 5 marks\n• Total Internal: 30 marks\n• End Semester Exam: 70 marks\n• Grand Total: 100 marks\nMinimum 40% in internals and 40% in semester exam required to pass.',
            'keywords': 'exam,pattern,marks,internal,external,cia,aat,mid'
        },
        {
            'category': 'Academics',
            'question': 'What is the minimum attendance requirement?',
            'answer': 'As per JNTUH regulations, a minimum of 75% attendance is mandatory in each subject to be eligible for end-semester exams. Students with less than 65% will be detained. Condonation may be granted for 65-75% attendance with a fee and valid reasons.',
            'keywords': 'attendance,minimum,required,percentage,detained,condonation'
        },
        {
            'category': 'Academics',
            'question': 'How to apply for revaluation?',
            'answer': 'Revaluation process:\n1) Apply within 15 days of results publication.\n2) Pay revaluation fee (₹1000 per subject) online.\n3) Submit the application at the exam branch.\n4) Results typically announced within 30 days.\nContact: exam@iare.ac.in',
            'keywords': 'revaluation,recounting,recheck,results,marks,correction'
        },
        {
            'category': 'Academics',
            'question': 'What is the CGPA calculation method?',
            'answer': 'CGPA = Sum of (Credit × Grade Point) for all subjects / Total Credits.\nGrade Points: O=10, A+=9, A=8, B+=7, B=6, C=5, F=0.\nPercentage = (CGPA - 0.75) × 10.\nExample: CGPA 8.5 = 77.5%',
            'keywords': 'cgpa,gpa,calculation,grade,percentage,convert'
        },
        {
            'category': 'Academics',
            'question': 'How to get my semester results?',
            'answer': 'Semester results can be accessed:\n1) JNTUH results portal: jntuhresults.in\n2) IARE student portal under "Results" section.\n3) Notice board in respective departments.\nKeep your hall ticket number ready for checking results.',
            'keywords': 'results,semester,marks,score,check,download'
        },
        {
            'category': 'Academics',
            'question': 'What are the elective subjects available?',
            'answer': 'Elective subjects are offered from 5th semester onwards.\n• Professional Electives: 5 electives across semesters 5-7\n• Open Electives: 2 electives from other departments\n• Skill-oriented courses: 2 courses\nEach department publishes the elective list before registration. Students choose based on interest and career goals.',
            'keywords': 'elective,optional,subject,choose,selection'
        },
        {
            'category': 'Academics',
            'question': 'What is the medium of instruction?',
            'answer': 'The medium of instruction at IARE is English for all programs. All examinations, assignments, and academic communications are conducted in English.',
            'keywords': 'medium,instruction,language,english'
        },

        # ── Hostel ──
        {
            'category': 'Hostel',
            'question': 'What are the hostel facilities at IARE?',
            'answer': 'IARE hostel facilities:\n• Separate hostels for boys and girls\n• AC and Non-AC rooms available\n• 24/7 security with CCTV surveillance\n• Wi-Fi connectivity\n• Hygienic mess with quality food (veg & non-veg)\n• RO purified drinking water\n• Laundry service\n• Recreation room with TV, indoor games\n• Gym facility\n• Study halls\n• Hot water supply\n• Medical assistance available',
            'keywords': 'hostel,accommodation,room,facility,amenity'
        },
        {
            'category': 'Hostel',
            'question': 'What is the hostel fee?',
            'answer': 'Hostel fee structure (approx.):\n• Non-AC Twin Sharing: ₹80,000/year\n• AC Twin Sharing: ₹1,00,000/year\n• Non-AC Triple Sharing: ₹65,000/year\nFee includes room, mess, maintenance, and Wi-Fi. Mess fee may be separately charged based on the plan selected.\nPayment: Per semester or annual.',
            'keywords': 'hostel,fee,cost,charges,room,rent,price'
        },
        {
            'category': 'Hostel',
            'question': 'How to apply for hostel?',
            'answer': 'Hostel admission process:\n1) Fill the hostel application form (available at admin office or portal).\n2) Submit with admission receipt and ID proof.\n3) Pay hostel fees.\n4) Collect room allotment on the reporting date.\nApply early as rooms are allotted on a first-come, first-served basis.\nContact: hostel@iare.ac.in',
            'keywords': 'hostel,apply,admission,book,room,allotment'
        },
        {
            'category': 'Hostel',
            'question': 'What are the hostel rules?',
            'answer': 'Key hostel rules:\n• Entry/exit timings: 6 AM - 9 PM\n• Visitors allowed only in the common area (10 AM - 5 PM)\n• Ragging is strictly prohibited\n• Alcohol, smoking, and drugs are banned\n• Electrical appliances (heaters, irons) not allowed in rooms\n• Students must sign the register while leaving/entering\n• Overnight stay outside requires prior written permission from warden\n• Maintain cleanliness in rooms and common areas',
            'keywords': 'hostel,rules,regulations,timing,policy,warden'
        },
        {
            'category': 'Hostel',
            'question': 'What is the mess menu?',
            'answer': 'Mess timings:\n• Breakfast: 7:30 AM - 9:00 AM\n• Lunch: 12:30 PM - 2:00 PM\n• Snacks: 4:30 PM - 5:30 PM\n• Dinner: 7:30 PM - 9:00 PM\n\nThe menu rotates weekly with variety in South Indian, North Indian, and continental items. Special meals on festivals. Veg and Non-Veg options available daily.',
            'keywords': 'mess,menu,food,breakfast,lunch,dinner,canteen'
        },

        # ── Library ──
        {
            'category': 'Library',
            'question': 'What are the library timings?',
            'answer': 'Library timings:\n• Working Days: 8:00 AM - 8:00 PM\n• Saturdays: 9:00 AM - 5:00 PM\n• Sundays & Holidays: Closed\n• Exam Period: Extended hours till 10:00 PM\nDigital library: Accessible 24/7 with student login.',
            'keywords': 'library,timing,hours,open,close,when'
        },
        {
            'category': 'Library',
            'question': 'How many books can I borrow?',
            'answer': 'Book borrowing limits:\n• B.Tech students: 4 books for 15 days\n• M.Tech students: 5 books for 15 days\n• Ph.D scholars: 8 books for 30 days\n• Faculty: 10 books for 30 days\nRenewal: Once for an additional 7 days (if no reservation). Late fine: ₹2/day/book.',
            'keywords': 'borrow,book,issue,limit,number,return,fine'
        },
        {
            'category': 'Library',
            'question': 'What digital resources does the library provide?',
            'answer': 'Digital library resources:\n• IEEE Xplore Digital Library\n• Springer Nature\n• ScienceDirect (Elsevier)\n• NPTEL Video Lectures\n• DELNET consortium access\n• J-Gate\n• NDL (National Digital Library)\n• ProQuest\n• Over 10,000+ e-books and 5,000+ e-journals\nAccess: Use student ID and password on the library portal.',
            'keywords': 'digital,library,ebook,journal,online,resource,database'
        },
        {
            'category': 'Library',
            'question': 'How to access the digital library?',
            'answer': 'To access the digital library:\n1) Visit library.iare.ac.in\n2) Login with your student ID and password\n3) Browse or search for resources\n4) Access e-books, journals, and research papers\nRemote access available through VPN for off-campus students.',
            'keywords': 'digital,library,access,login,online,ebook'
        },

        # ── Fees & Scholarships ──
        {
            'category': 'Fees',
            'question': 'What is the fee structure for B.Tech?',
            'answer': 'B.Tech fee structure (approx. per year):\n• Tuition Fee (Convener Quota): ₹1,01,000\n• Tuition Fee (Management Quota): ₹1,60,000\n• Special Fee: ₹15,000 (includes exam, library, lab)\n• Caution Deposit: ₹5,000 (one-time, refundable)\nPayment modes: Online (student portal), DD, or bank challan.',
            'keywords': 'fee,tuition,cost,payment,amount,charges,structure'
        },
        {
            'category': 'Fees',
            'question': 'What scholarships are available?',
            'answer': 'Scholarships at IARE:\n• TS Government Scholarship (SC/ST/BC/EBC/Minority)\n• AP Government Scholarship (for AP students)\n• Merit Scholarship (top rankers in EAMCET)\n• Management Merit Scholarship (based on academic performance)\n• National Scholarship Portal (NSP)\n• Central Sector Scholarship\n• AICTE Pragati Scholarship (for girls)\nApply through the respective government portals. Contact: scholarships@iare.ac.in',
            'keywords': 'scholarship,financial,aid,merit,government,fee,waiver'
        },
        {
            'category': 'Fees',
            'question': 'How to pay fees online?',
            'answer': 'Online fee payment steps:\n1) Login to student portal (portal.iare.ac.in)\n2) Go to "Fee Payment" section\n3) Select the fee type and semester\n4) Choose payment method (Net Banking, UPI, Credit/Debit Card)\n5) Complete payment and download receipt\nFor issues: accounts@iare.ac.in or 040-24680600.',
            'keywords': 'pay,fee,online,portal,payment,method,receipt'
        },
        {
            'category': 'Fees',
            'question': 'Is there an education loan facility?',
            'answer': 'Yes, IARE assists students in obtaining education loans:\n• Tie-ups with SBI, Canara Bank, Bank of Baroda, HDFC Credila\n• Loan covers tuition, hostel, and living expenses\n• Interest rates: 8-12% depending on the bank\n• Documents: Admission letter, fee structure, income proof, collateral (for loans > ₹7.5 lakh)\nContact the accounts office for loan facilitation letters.',
            'keywords': 'loan,education,bank,finance,emi,interest'
        },

        # ── Events ──
        {
            'category': 'Events',
            'question': 'What major events are held at IARE?',
            'answer': 'Major annual events at IARE:\n• Technozion - Annual Technical Fest (March)\n• Spectra - Cultural Fest (February)\n• Aeroquest - Aeronautical Symposium\n• Hack-a-thon - Coding competition\n• Sports Day - Inter-department sports (January)\n• Engineers Day Celebrations (September 15)\n• Graduation Day\n• Freshers Day\n• National-level workshops and seminars\nFollow: events@iare.ac.in for updates.',
            'keywords': 'event,fest,cultural,technical,competition,workshop'
        },
        {
            'category': 'Events',
            'question': 'How to participate in college events?',
            'answer': 'To participate in events:\n1) Watch for announcements on notice boards and student portal\n2) Register through the event registration link\n3) Pay registration fee (if any)\n4) Attend briefing sessions\n5) Participate and win prizes!\nYou can also volunteer to organize events through student clubs.',
            'keywords': 'participate,event,register,join,competition'
        },
        {
            'category': 'Events',
            'question': 'What student clubs are available?',
            'answer': 'IARE student clubs:\n• Coding Club - Competitive programming\n• Robotics Club - Automation & IoT projects\n• Literary Club - Debate, quiz, writing\n• Cultural Club - Dance, music, drama\n• Photography Club\n• NSS (National Service Scheme)\n• NCC (National Cadet Corps)\n• Entrepreneurship Cell (E-Cell)\n• IEEE Student Branch\n• CSI Student Chapter\n• ACM Student Chapter\nJoin through the student affairs office.',
            'keywords': 'club,society,extra,curricular,activity,student,organization'
        },

        # ── Transport ──
        {
            'category': 'Transport',
            'question': 'What are the bus routes available?',
            'answer': 'IARE bus routes cover major areas in Hyderabad:\n• Route 1: Secunderabad - Kompally - IARE\n• Route 2: Kukatpally - BHEL - IARE\n• Route 3: Dilsukhnagar - LB Nagar - IARE\n• Route 4: Mehdipatnam - Tolichowki - IARE\n• Route 5: Ameerpet - SR Nagar - IARE\n• Route 6: ECIL - AS Rao Nagar - IARE\n• Route 7: Miyapur - Chandanagar - IARE\n• Route 8: Uppal - Nacharam - IARE\n• And 12+ more routes\nContact: transport@iare.ac.in',
            'keywords': 'bus,route,transport,pickup,stop,area'
        },
        {
            'category': 'Transport',
            'question': 'What is the transport fee?',
            'answer': 'Transport fee varies by distance:\n• Up to 15 km: ₹35,000/year\n• 15-25 km: ₹45,000/year\n• 25-40 km: ₹55,000/year\n• Above 40 km: ₹65,000/year\nPayment: Per semester or annual. Fee includes both pickup and drop.\nContact: transport@iare.ac.in',
            'keywords': 'transport,bus,fee,cost,charges,price'
        },
        {
            'category': 'Transport',
            'question': 'What are the bus timings?',
            'answer': 'Bus timings:\n• Morning pickup: 7:00 AM - 8:30 AM (varies by route)\n• College arrival: By 9:00 AM\n• Evening departure: 4:45 PM from campus\n• Saturday: Regular timing, departure at 1:00 PM\nBuses are GPS tracked. Download the IARE app for live tracking.',
            'keywords': 'bus,timing,schedule,morning,evening,departure'
        },

        # ── WiFi & IT ──
        {
            'category': 'WiFi',
            'question': 'How to connect to campus WiFi?',
            'answer': 'Campus WiFi connection:\n• SSID: IARE-Student (for students) or IARE-Faculty (for faculty)\n• Username: Your Student/Employee ID\n• Password: Same as student portal password\n• Coverage: All academic blocks, library, hostel\n• Speed: Up to 100 Mbps\nTroubleshooting: ithelpdesk@iare.ac.in or ext. 234',
            'keywords': 'wifi,connect,internet,network,login,password,ssid'
        },
        {
            'category': 'WiFi',
            'question': 'WiFi is not working, what should I do?',
            'answer': 'WiFi troubleshooting steps:\n1) Forget the IARE network and reconnect\n2) Restart your device\n3) Make sure you are using correct credentials\n4) Check if your account is active on the portal\n5) Move closer to an access point\n6) Clear browser cache if using captive portal\nIf issue persists, contact IT Helpdesk:\n• Email: ithelpdesk@iare.ac.in\n• Phone: Ext. 234\n• Location: IT Block, Room 102',
            'keywords': 'wifi,not,working,problem,issue,slow,disconnect'
        },

        # ── Labs & Facilities ──
        {
            'category': 'Facilities',
            'question': 'What labs are available at IARE?',
            'answer': 'IARE labs include:\n• CSE: Programming Lab, Networks Lab, AI/ML Lab, Cyber Security Lab, Cloud Computing Lab\n• ECE: VLSI Lab, Embedded Systems Lab, Communication Lab, Microprocessor Lab\n• EEE: Machines Lab, Power Electronics Lab, Control Systems Lab\n• MECH: CAD/CAM Lab, Thermal Engineering Lab, Workshop\n• CIVIL: Surveying Lab, Material Testing Lab, CAD Lab\n• General: Physics Lab, Chemistry Lab, English Language Lab\nAll labs have modern equipment and licensed software.',
            'keywords': 'lab,laboratory,computer,workshop,practical,equipment'
        },
        {
            'category': 'Facilities',
            'question': 'Does campus have medical facilities?',
            'answer': 'Yes, IARE has a medical center on campus:\n• Qualified doctor available from 9 AM - 5 PM\n• Nursing staff available throughout the day\n• First Aid facility 24/7\n• Ambulance on standby for emergencies\n• Tie-up with nearby hospitals (Apollo, Medicover, KIMS)\n• Regular health check-ups for hostel students\n• Counselling services available\nLocation: Near Admin Block, Ground Floor.',
            'keywords': 'medical,health,doctor,hospital,emergency,clinic'
        },
        {
            'category': 'Facilities',
            'question': 'What sports facilities are available?',
            'answer': 'IARE sports facilities:\n• Cricket ground with practice nets\n• Football ground\n• Basketball court (2)\n• Volleyball court (2)\n• Badminton courts (indoor, 4)\n• Tennis court\n• Table Tennis (6 tables)\n• Chess room\n• Gymnasium with modern equipment\n• Athletics track (200m)\n• Kabaddi & Kho-Kho grounds\n• Yoga & meditation hall\nCoaches available for all major sports. Inter-college tournaments hosted annually.',
            'keywords': 'sports,games,gym,fitness,athletics,ground,court'
        },
        {
            'category': 'Facilities',
            'question': 'Is there a canteen on campus?',
            'answer': 'Yes, IARE has multiple food outlets:\n• Main Canteen (near Admin Block) - Meals, snacks, beverages\n• Food Court - Multiple stalls with variety\n• Juice Corner\n• Coffee & Tea kiosks in each block\nTimings: 8:00 AM - 6:00 PM\nPrices are subsidized for students. Both veg and non-veg options available.',
            'keywords': 'canteen,food,eat,snack,restaurant,cafeteria'
        },
        {
            'category': 'Facilities',
            'question': 'Is there a bank/ATM on campus?',
            'answer': 'Banking facilities on campus:\n• SBI ATM located near the main gate\n• Canara Bank extension counter (operates Tue & Thu, 11 AM - 2 PM)\n• Online banking kiosks in the library\n• Fee payment counter at the accounts office\nNearest full-service bank branches are located in Dundigal village (1 km from campus).',
            'keywords': 'bank,atm,money,cash,withdrawal,sbi'
        },

        # ── Contact ──
        {
            'category': 'Contact',
            'question': 'What is the college contact number?',
            'answer': 'IARE Contact Information:\n• Main Office: 040-24680600\n• Admissions: 040-24680611\n• Accounts: 040-24680622\n• Principal Office: 040-24680601\n• Exam Branch: 040-24680633\n• Hostel: 040-24680644\n• Transport: 040-24680655\n• Toll-free: 1800-425-8555\nEmail: info@iare.ac.in\nWebsite: www.iare.ac.in',
            'keywords': 'contact,phone,number,call,reach,office,telephone'
        },
        {
            'category': 'Contact',
            'question': 'What is the college email address?',
            'answer': 'IARE email addresses:\n• General Enquiry: info@iare.ac.in\n• Admissions: admissions@iare.ac.in\n• Principal: principal@iare.ac.in\n• Exam Branch: exam@iare.ac.in\n• Placements: placements@iare.ac.in\n• Accounts: accounts@iare.ac.in\n• IT Helpdesk: ithelpdesk@iare.ac.in\n• Hostel: hostel@iare.ac.in\n• Transport: transport@iare.ac.in',
            'keywords': 'email,mail,id,address,contact,write'
        },

        # ── Certifications & Training ──
        {
            'category': 'Academics',
            'question': 'What certifications can I pursue at IARE?',
            'answer': 'IARE supports various certification programs:\n• AWS Cloud Practitioner\n• Microsoft Azure Fundamentals\n• Google IT Support\n• Cisco CCNA\n• Oracle Java Certification\n• SAS Programming\n• NPTEL Swayam Courses (with JNTUH credit transfer)\n• Coursera/edX MOOCs\n• Red Hat Linux Administration\nMany certifications have subsidized exam fees through college partnerships.',
            'keywords': 'certification,certificate,course,training,skill,online'
        },
        {
            'category': 'Academics',
            'question': 'What research opportunities are available?',
            'answer': 'Research opportunities at IARE:\n• Funded research projects under DST, AICTE, UGC\n• Student research programs\n• Research labs: AI/ML Research Lab, IoT Lab, Cyber Security Research Center\n• Paper publication support (IEEE, Springer, Elsevier journals)\n• International conference participation (travel grants available)\n• Industry-collaborated R&D projects\n• Innovation and Incubation Center\nContact your department HOD for guidance.',
            'keywords': 'research,project,paper,publication,journal,conference,phd'
        },

        # ── Student Services ──
        {
            'category': 'General',
            'question': 'How to access the student portal?',
            'answer': 'Student Portal access:\n• URL: portal.iare.ac.in\n• Username: Your Roll Number (e.g., 23951A62B0)\n• Default Password: Your Date of Birth (DDMMYYYY)\n• Features: Attendance, Marks, Fee Payment, Timetable, Notices\nIf locked out, contact your department office or email: ithelpdesk@iare.ac.in',
            'keywords': 'portal,student,login,access,online,website'
        },
        {
            'category': 'General',
            'question': 'How to get ID card replacement?',
            'answer': 'ID card replacement process:\n1) Submit application at Admin Office \n2) Attach a passport-size photograph\n3) Pay replacement fee: ₹200\n4) New ID card will be issued within 5-7 working days.\nKeep your ID card safe - it is required for entry and all campus services.',
            'keywords': 'id,card,identity,lost,replacement,new'
        },
        {
            'category': 'General',
            'question': 'What is the grievance redressal process?',
            'answer': 'Grievance Redressal:\n1) Submit complaint via the online grievance portal\n2) Or write to grievance@iare.ac.in\n3) The Grievance Redressal Committee will acknowledge within 48 hours\n4) Resolution timeline: 7-15 working days\n5) Escalation: Dean of Student Affairs → Vice Principal → Principal\nAnonymous complaints are also accepted through the suggestion box at Admin Block.',
            'keywords': 'grievance,complaint,problem,issue,redressal,resolve'
        }
    ]
    
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'campus_assistant.db'))
        c = conn.cursor()
        
        # Check if FAQs already exist
        c.execute('SELECT COUNT(*) FROM faqs')
        count = c.fetchone()[0]
        
        if count == 0:
            for faq in default_faqs:
                c.execute('''INSERT INTO faqs (category, question, answer, keywords)
                             VALUES (?, ?, ?, ?)''',
                          (faq['category'], faq['question'], faq['answer'], faq['keywords']))
            conn.commit()
            print("✅ Default FAQs initialized")
        
        conn.close()
    except Exception as e:
        print(f"Error initializing FAQs: {e}")

if __name__ == "__main__":
    init_default_faqs()
    chatbot = CampusChatbot()
    
    # Test the chatbot
    test_messages = [
        "Hello",
        "Tell me about admissions",
        "What are the placement statistics?",
        "Library hours?",
        "How to apply for hostel?"
    ]
    
    print("\n🤖 Testing Chatbot Engine\n" + "="*50)
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = chatbot.get_response(msg)
        print(f"🤖 Bot: {response['response']}")
        print(f"   Intent: {response['intent']} (Confidence: {response['confidence']})")
