from smtplib import SMTP_SSL, SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from multi_tenant.settings import ENDPOINT_URL

def send_email(email,token):
    # Replace sender@example.com with your "From" address.
    # This address must be verified.
    SENDER = 'mayur.nawghare@we360.ai'
    SENDERNAME = 'Mayur '
    
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.

    # Replace smtp_username with your Amazon SES SMTP user name.
    USERNAME_SMTP = "mayur.nawghare@we360.ai"
    
    # Replace smtp_password with your Amazon SES SMTP password.
    PASSWORD_SMTP = "ihngtiylzjxhtqcu"
    
    # (Optional) the name of a configuration set to use for this message.
    # If you comment out this line, you also need to remove or comment out
    # the "X-SES-CONFIGURATION-SET:" header below.
    # CONFIGURATION_SET = "ConfigSet"
    
    # If you're using Amazon SES in an AWS Region other than US West (Oregon),
    # replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
    # endpoint in the appropriate region.
    HOST = "smtp.gmail.com"
    PORT = 465
    
    # The subject line of the email.
    SUBJECT = "Account Verification Link"
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Verify your email\r\n"
                 "Setup your account "
                 )

    BODY_HTML = f'''
        <!doctype html>
        <html lang="en">
        <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

            <!-- Bootstrap CSS -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

            <title>Verify account</title>
        </head>
        <body>
            <h1>Verify your account</h1>


            <a href={ENDPOINT_URL+"verify/account/"+token}>Click here to setup profile</a>

            
        </body>
        </html>
   '''
    
 
   
        # Replace recipient@example.com with a "To" address. If your account
        # is still in the sandbox, this address must be verified.
    RECIPIENT = email
  
    # The HTML body of the email.
    

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT
    # Comment or delete the next line if you are not using a configuration set
    # msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(BODY_TEXT, 'plain')
    part2 = MIMEText(BODY_HTML, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
        
    # Try to send the message.
    try:
        with SMTP_SSL(HOST, PORT) as server:
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
            print("Email sent!")
            return True
    
    except SMTPException as e:
        print("Error: ", e)
        return False