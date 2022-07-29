import smtplib

HOST = "mx1.pstu.ru"
SUBJECT = "Test email from Python"
TO = "romagrizly@gmail.com"
FROM = "gofpmm@pstu.ru"
text = "Python 3.4 rules them all!"

BODY = "\r\n".join((
    "From: %s" % FROM,
    "To: %s" % TO,
    "Subject: %s" % SUBJECT,
    "",
    text
))

server = smtplib.SMTP(HOST)
server.login("local\ANPodsedercev", "exJVyIF3")
server.sendmail(FROM, [TO], BODY)
server.quit()