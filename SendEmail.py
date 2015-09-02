import sendgrid,datetime
import csv




#grab all emails to send. 
emailList = []
with open ("email1.csv", "rU") as emails:
	emailReader = csv.reader(emails, delimiter=',')
	for row in emailReader:
		emailList.append(row[0])


sg = sendgrid.SendGridClient('stavrop', 'Koalas12')

message = sendgrid.Mail()
message.add_bcc("brandonongnz@gmail.com")

subject = "Reminder - #spotted Photo Competition with Prizes to Win!"
message.set_subject(subject)

with open ("instagram.html", "r") as reportFile:
	htmlMessage = reportFile.read()


message.set_html(htmlMessage)
message.set_from('Ripple <wellripplemethis@gmail.com>')
status, msg = sg.send(message)
