import mechanize
from mechanize import ParseResponse, urlopen, urljoin
import cgi
import os
import getpass

#Courses registered, read from courses.txt file.
list_courses = list()

coursesfile = open( "courses.txt", "r" )
for line in coursesfile:
    list_courses.append(line.replace("\n", "").replace("\r",""))    
coursesfile.close()

for directory in list_courses:
	if not os.path.exists("Moodle/" + directory):
		os.makedirs("Moodle/" + directory)

#Create a mechanize web navigator
browser = mechanize.Browser()

#Open moodle login page and select login form
browser.open("http://10.1.1.242/moodle/login/index.php");

flag = 0
#Enter login details into form and submit
while flag == 0:
	username = raw_input("Username:")
	password = getpass.getpass()
	browser.select_form(nr = 0)
	browser.form["username"] = username
	browser.form["password"] = password
	browser.submit()
	flag = 1
	if "login/index.php" in browser.geturl():
		print "Please enter correct details."
		flag = 0

#Check for the courses pages on the website
mainpage_links = list(browser.links())

print "Downloading....."
for link_course in mainpage_links:
	for course in list_courses:
		if link_course.text == course:	#If found, open course
			req_open_course = browser.click_link(url=link_course.url)
			browser.open(req_open_course)
			incourse_links = list(browser.links())
			
			list_filelinks = list()
			list_folderlinks = list()
			
			for link_file in incourse_links:
				#Files check
				if "resource" in link_file.url:
					list_filelinks.append(link_file.url)
					req_open_file = browser.click_link(url=link_file.url)
					res = browser.open(req_open_file)
					try:
						_, params = cgi.parse_header(res.info().get('Content-Disposition', ''))
						filename = params['filename']
						browser.back()
						req_to_download = browser.click_link(url=link_file.url)
						browser.retrieve(req_open_file, "Moodle/" + course + "/" + filename)
					except:
						browser.open(req_open_file)
						download_links = browser.links()
						for link_download in download_links:
							if ".pdf" in link_download.text:
								req_to_download = browser.click_link(url=link_download.url)
								filename = link_download.text.rsplit("[IMG]")[-1]
								browser.retrieve(req_to_download, "Moodle/" + course + "/" + filename)
						browser.back()
						browser.back()
						
			folders = list()			
			for link_folder in incourse_links:
				#Folder check
				if link_folder.text[0:6] == "Folder":
					list_folderlinks.append(link_folder.url)
					folders.append(link_folder.text[11:].replace(":"," "))
					if not os.path.exists("Moodle/" + course + "/" + link_folder.text[11:].replace(":"," ")):
						os.makedirs("Moodle/" + course + "/" + (link_folder.text[11:]).replace(":"," "))
						
			index = 0		
			for link_open_folder in list_folderlinks:
				req_open_folder = browser.click_link(url=link_open_folder)
				browser.open(req_open_folder)
				list_folderfilelinks = list(browser.links())
				list_folderfileurls =  list()
				for link_file in list_folderfilelinks: #Inside file check
					if ".pdf" in link_file.text or ".doc" in link_file.text or ".ppt" in link_file.text or ".xls" in link_file.text:
						req_to_download = browser.click_link(url=link_file.url)
						filename = link_file.text.rsplit("[IMG]")[-1]
						browser.retrieve(req_to_download, "Moodle/" + course + "/" + folders[index] + "/" + filename)
					if link_file.text[0:4] == "File":
						list_folderfileurls.append(link_file.url)
				for link_to_file in list_folderfileurls:
					req_open_file = browser.click_link(url=link_to_file)
					browser.open(req_open_file)
					download_links = browser.links()
					for link_download in download_links:
						if ".pdf" in link_download.text or ".doc" in link_download.text or ".ppt" in link_download.text or ".xls" in link_download.text:
							req_to_download = browser.click_link(url=link_download.url)
							filename = link_download.text.rsplit("[IMG]")[-1]
							browser.retrieve(req_to_download, "Moodle/" + course + "/" + folders[index] + "/" + filename)
					browser.back()
				index = index + 1
				browser.back()
			browser.back()	
print "\nCompleted!"