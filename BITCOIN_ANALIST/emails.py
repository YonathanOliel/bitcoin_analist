import smtplib
import emails_config



def sending_the_emails(address, message):
    server_mail = smtplib.SMTP(emails_config.config_server, emails_config.config_server_port)
    server_mail.starttls()
    server_mail.login(emails_config.config_email, emails_config.config_password)
    server_mail.sendmail(emails_config.config_email, address, message)
    server_mail.quit()



