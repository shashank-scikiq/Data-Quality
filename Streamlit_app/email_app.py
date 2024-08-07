api_url = "http://127.0.0.1:8000/dashboard/api/key_insights/"
sender_email = "donotreply@ondc.org"
receiver_email = "shashank.katyayan@ondc.org"
password = ""  # Consider using environment variables for security
subject = "Daily Data Summary"


import requests

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def fetch_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def send_email_with_inline_images(subject, sender_email, receiver_email, password, html_content, images):
    # Create the root message and fill in the from, to, and subject headers
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(html_content, 'html')
    msgAlternative.attach(msgText)

    # Attach images
    for cid, img_path in images.items():
        with open(img_path, 'rb') as file:
            msg_image = MIMEImage(file.read())
            # Define the image's ID as referenced above
            msg_image.add_header('Content-ID', f'<{cid}>')
            msg.attach(msg_image)

    # Send the email via SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")



def format_email_content(html_file_path, data):
    """Reads an HTML template file and formats it with data."""
    with open(html_file_path, 'r', encoding='utf-8') as file:
        email_template = file.read()
    
    
        # weekly_trend_image=data.get('weekly_trend_image', '#'),
        # monthly_trend_image=data.get('monthly_trend_image', '#'),
        # key_insight_image=data.get('key_insight_image', '#'),
        
    print(data)
    # formatted_email = email_template.format(
    #     percentage_seller=data.get('percentage_seller', 'N/A'),
    #     percentage_of_orders=data.get('state_order_volume_weekwise', 'N/A'),
    #     state_name=data.get('state_order_volume', 'N/A'),
    #     delta_volume_max_state=data.get('district_order_volume', 'N/A'),
    #     current_period=data.get('current_period', 'N/A'),
    #     state_order_volume=data.get('state_order_volume', 'N/A'),
    #     district_order_volume=data.get('district_order_volume', 'N/A'),
    #     subcategory_order_volume=data.get('subcategory_order_volume', 'N/A'),
    #     # Add more data replacements as needed
    # )
    formatted_email = email_template.format(
        # percentage_seller=data['seller_card'].get('percentage_seller', 'N/A'),


        current_wtd_period=data['state_order_volume_weekwise'].get('current_period', 'N/A'),
        previous_wtd_period=data['state_order_volume_weekwise'].get('previous_period', 'N/A'),

        percentage_of_orders=data['state_order_volume_weekwise'].get('delta_volume_max_state', 'N/A'),
        state_name_weekly=data['state_order_volume_weekwise'].get('state_name', 'N/A'),

        percentage_of_orders_weekly=data['district_order_volume_weekwise'].get('delta_volume_max_state', 'N/A'),
        district_name_weekly=data['district_order_volume_weekwise'].get('district_name', 'N/A'),




        current_period=data['state_order_volume'].get('current_period', 'N/A'),
        previous_period=data['state_order_volume'].get('previous_period', 'N/A'),

        percentage_of_orders_monthly=data['state_order_volume'].get('delta_volume_max_state', 'N/A'),
        state_name_monthly=data['state_order_volume'].get('state_name', 'N/A'),

        percentage_of_district_orders_monthly=data['district_order_volume'].get('delta_volume_max_state', 'N/A'),
        district_name_monthly=data['district_order_volume'].get('district_name', 'N/A'),
        
        seller_percentage=data['seller_card'].get('percentage_seller', 'N/A'),
        orders_percentage=data['seller_card'].get('percentage_of_orders', 'N/A'),

        # state_order_volume=data['state_order_volume'].get('state_name', 'N/A'),
        # district_order_volume=data['district_order_volume'].get('delta_volume_max_state', 'N/A'),
        # subcategory_order_volume=data['subcategory_order_volume'].get('delta_volume_max_subcat', 'N/A'),
        # Adjusted data access according to the provided data structure
    )



    return formatted_email
        

# # HTML content with the images referenced by their CIDs
# html_content = """
# Your HTML content here, with img tags like:
# <img src="cid:image1"> for each image you want to embed inline.
# """

data = fetch_data(api_url)


# Dictionary mapping CIDs to local image paths
images = {
    'logo_img': './email_smtp/ondc_logo.png',
    'attention_img': './email_smtp/attention.png',
    'weekly_trend_img': './email_smtp/weekly_trend.png',
    'monthly_trend_img': './email_smtp/monthly_trend.png',
    'key_insights_img': './email_smtp/keyinsight.png',
    'dashboard_img': './email_smtp/dashboard.png',
    # Add paths and CIDs for 'weekly_trend.png', 'monthly_trend.png', 'keyinsight.png', 'dashboard.png' as well
}

if data:
    html_content = format_email_content('./email_smtp/email_management_template.html', data)


# Call the function with your email details
send_email_with_inline_images(
    subject=subject,
    sender_email=sender_email,
    receiver_email=receiver_email,
    password=password,
    html_content=html_content,
    images=images
)




# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.image import MIMEImage

# import requests


# def get_mime_type(file_path):
#     import mimetypes
#     mime_type, _ = mimetypes.guess_type(file_path)
#     if mime_type is None:
#         raise ValueError(f"Could not guess MIME type for {file_path}")
#     return mime_type.split('/')[1]  # Return the subtype after '/'


# from email.mime.image import MIMEImage

# def attach_image(msg, cid, image_path):
#     mime_subtype = get_mime_type(image_path)  # Get the MIME subtype
#     with open(image_path, 'rb') as file:
#         msg_image = MIMEImage(file.read(), _subtype=mime_subtype)
#         msg_image.add_header('Content-ID', f'<{cid}>')
#         msg.attach(msg_image)



# def fetch_data(api_url):
#     response = requests.get(api_url)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         return None


# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# # def send_email_with_images(subject, html_content, sender_email, receiver_email, password, image_paths):
# #     msg = MIMEMultipart('related')  # Use 'related' to indicate embedded images
# #     msg['Subject'] = subject
# #     msg['From'] = sender_email
# #     msg['To'] = receiver_email

# #     msg.attach(MIMEText(html_content, 'html'))

# #     for cid, image_path in image_paths.items():
# #         attach_image(msg, cid, image_path)

# #     try:
# #         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# #         server.login(sender_email, password)
# #         server.sendmail(sender_email, receiver_email, msg.as_string())
# #         server.quit()
# #         print("Email sent successfully!")
# #     except Exception as e:
# #         print(f"Failed to send email. Error: {e}")


# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# def send_email(subject, html_content, sender_email, receiver_email, password):
#     """Sends an email with HTML content."""
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = subject
#     msg['From'] = sender_email
#     msg['To'] = receiver_email

#     part = MIMEText(html_content, 'html')
#     msg.attach(part)

#     try:
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, msg.as_string())
#         server.quit()
#         print("Email sent successfully!")
#     except Exception as e:
#         print(f"Failed to send email. Error: {e}")





# def send_email_with_images(subject, html_content, sender_email, receiver_email, password, image_paths):
#     msg = MIMEMultipart('related')  # Use 'related' to indicate embedded images
#     msg['Subject'] = subject
#     msg['From'] = sender_email
#     msg['To'] = receiver_email

#     msg.attach(MIMEText(html_content, 'html'))

#     for cid, image_path in image_paths.items():
#         with open(image_path, 'rb') as file:
#             msg_image = MIMEImage(file.read())
#             msg_image.add_header('Content-ID', f'<{cid}>')
#             msg.attach(msg_image)

#     try:
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, msg.as_string())
#         server.quit()
#         print("Email sent successfully!")
#     except Exception as e:
#         print(f"Failed to send email. Error: {e}")



# def send_email(subject, html_content, sender_email, receiver_email, password):
#     """Sends an email with HTML content."""
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = subject
#     msg['From'] = sender_email
#     msg['To'] = receiver_email

#     part = MIMEText(html_content, 'html')
#     msg.attach(part)

#     try:
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, msg.as_string())
#         server.quit()
#         print("Email sent successfully!")
#     except Exception as e:
#         print(f"Failed to send email. Error: {e}")

# def format_email_content(html_file_path, data):
#     """Formats the email content by injecting data into the HTML template."""
#     with open(html_file_path, 'r', encoding='utf-8') as file:
#         email_template = file.read()

#     # Use your actual image URLs here
#     seller_icon_url = "https://example.com/path/to/seller_icon.png"
#     weekly_trend_image = "https://example.com/path/to/weekly_trend.png"
#     monthly_trend_image = "https://example.com/path/to/monthly_trend.png"
#     key_insight_image = "https://example.com/path/to/keyinsight.png"
#     dashboard_image = "https://example.com/path/to/dashboard.png"

#     formatted_email = email_template.format(
#         seller_icon_url=seller_icon_url,
#         weekly_trend_image=weekly_trend_image,
#         monthly_trend_image=monthly_trend_image,
#         key_insight_image=key_insight_image,
#         dashboard_image=dashboard_image,
#         percentage_seller=data.get('percentage_seller', 'N/A'),
#         percentage_of_orders=data.get('percentage_of_orders', 'N/A'),
#         state_name=data.get('state_name', 'N/A'),
#         delta_volume_max_state=data.get('delta_volume_max_state', 'N/A'),
#         current_period=data.get('current_period', 'N/A'),
#         state_order_volume=data.get('state_order_volume', 'N/A'),
#         district_order_volume=data.get('district_order_volume', 'N/A'),
#         subcategory_order_volume=data.get('subcategory_order_volume', 'N/A'),
#         # Add other placeholders and data replacements as needed
#     )
#     return formatted_email


# data = fetch_data(api_url)
# image_paths = {
# 'logo_url': 'http://15.206.0.116:8081/static/assets/img/ondc_logo.svg'
#     }

# print(data)
# if data:
#     html_content = format_email_content('./email_management_template.html', data)

#     send_email_with_images(subject, html_content, sender_email, receiver_email, password, image_paths)

#     # send_email(subject, html_content, sender_email, receiver_email, password)

#     # send_email(sender_email, receiver_email, subject, email_content, password)
# else:
#     print("Failed to fetch data.")