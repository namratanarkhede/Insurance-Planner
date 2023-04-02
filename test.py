import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

my_email = "insurance.notifier@yahoo.com"
password = "mgjrrdjhwxuwoctu"

message = """

        <html>
                	<head>
                		<meta charset="utf-8" />
                		<title></title>
                		<style>
                		    a {
                                text-decoration: none;
                              }
                			.invoice-box {
                				max-width: 800px;
                				margin: auto;
                				padding: 30px;
                				border: 1px solid #eee;
                				box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
                				font-size: 16px;
                				line-height: 24px;
                				font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
                				color: #555;
                			}
                			.invoice-box table {
                				width: 100%;
                				line-height: inherit;
                				text-align: left;
                			}
                			.invoice-box table td {
                				padding: 5px;
                				vertical-align: top;
                			}
                			.invoice-box table tr td:nth-child(2) {
                				text-align: right;
                			}
                			.invoice-box table tr.top table td {
                				padding-bottom: 20px;
                			}
                			.invoice-box table tr.top table td.title {
                				font-size: 45px;
                				line-height: 45px;
                				color: #333;
                			}
                			.invoice-box table tr.information table td {
                				padding-bottom: 40px;
                			}
                          .idno{
                          	font-weight: bold;
                            font-size: 60px;
                            padding-top:70px;
                            text-align: center;
                          }
                          .invoiceid{
                          	text-align: center;
                          }
                			.invoice-box table tr.heading td {
                				background: #eee;
                				border-bottom: 1px solid #ddd;
                				font-weight: bold;
                			}
                			.invoice-box table tr.details td {
                				padding-bottom: 20px;
                			}
                			.invoice-box table tr.item td {
                				border-bottom: 1px solid #eee;
                			}
                			.invoice-box table tr.item.last td {
                				border-bottom: none;
                			}
                			.invoice-box table tr.total td:nth-child(2) {
                				border-top: 2px solid #eee;
                				font-weight: bold;
                			}
                			@media only screen and (max-width: 600px) {
                				.invoice-box table tr.top table td {
                					width: 100%;
                					display: block;
                					text-align: center;
                				}
                				.invoice-box table tr.information table td {
                					width: 100%;
                					display: block;
                					text-align: center;
                				}
                			}
                			/** RTL **/
                			.invoice-box.rtl {
                				direction: rtl;
                				font-family: Tahoma, 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
                			}
                			.invoice-box.rtl table {
                				text-align: right;
                			}
                			.invoice-box.rtl table tr td:nth-child(2) {
                				text-align: left;
                			}
                		</style>
                	</head>
                	<body>
                		<div class="invoice-box">
                			<table cellpadding="0" cellspacing="0">
                				<tr class="top">
                					<td colspan="2">
                						<table>
                							<tr>
                								<td class="title">
                									<img src = "https://tse4.mm.bing.net/th?id=OIP.jj3q0BXl_mZZWq4UjDRRgQAAAA&pid=Api&P=0&w=157&h=157" style="width: 100%; max-width: 150px" />
                								</td>
                								<td>
                                                  <table>
                                                    <tr class>
                                                      <td class="invoiceid">Insurance Planner</td>
                                                    </tr>
                                                    <tr>
                                                      <td class="idno"></td>
                                                    </tr>
                                                  </table>
                								</td>
                							</tr>
                						</table>
                					</td>
                				</tr>
                				<tr class="information heading">
                					<td colspan="2">
                						<table>
                							<tr>
                								<td>
                									Contact Us
                								</td>
                							<td>
                									insurance.notifier@yahoo.com
                								</td>
                							</tr>
                						</table>
                					</td>
                				</tr>

                			</table>
        					<p>Hi<br>Your KYC has been rejected. The team's response was<br>
        						<br>Regards,<br><a href="/">Insurance Planner</a></p>
                		</div>
                	</body>
                </html>

            """
with smtplib.SMTP("smtp.mail.yahoo.com") as smtp:
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(message, 'html'))
    msg['Subject'] = 'KYC Rejection Email'
    msg['From'] = my_email
    msg['To'] = "somiyapanikar@gmail.com"
    smtp.starttls()
    smtp.login(user=my_email, password=password)
    smtp.sendmail(
        from_addr=my_email,
        to_addrs="somiyapanikar@gmail.com",
        msg=msg.as_string()
    )
