# from django.core.mail.backends.smtp import EmailBackend
# import smtplib

# class CustomEmailBackend(EmailBackend):
#     def _send(self, email_message):
#         """A helper method that does the actual sending."""
#         if not email_message.recipients():
#             return False

#         try:
#             self.open()
#             if not self.connection:
#                 # Failed silently.
#                 return False
#             self.connection.sendmail(
#                 email_message.from_email,
#                 email_message.recipients(),
#                 email_message.message().as_bytes(),
#             )
#         except smtplib.SMTPException as e:
#             if not self.fail_silently:
#                 raise
#             return False
#         return True

#     def open(self):
#         """Ensures we have a connection to the email server."""
#         if self.connection:
#             return False

#         try:
#             self.connection = self.connection_class(
#                 self.host, self.port, **self.connection_params
#             )
#             self.connection.ehlo()
#             if self.use_tls:
#                 # Explicitly call starttls without keyfile and certfile
#                 self.connection.starttls()
#                 self.connection.ehlo()
#             if self.username and self.password:
#                 self.connection.login(self.username, self.password)
#             return True
#         except smtplib.SMTPException:
#             if not self.fail_silently:
#                 raise
#         return False
