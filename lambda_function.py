import json
import base64
import tempfile
import os

import boto3
from docx2pdf import convert

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # TODO implement
    print(event)
    
    file_content = base64.b64decode(event['body'])
    
    # Check if the file is in DOCX format
    is_docx = is_file_docx(file_content)
    
    # Check if the file size is valid
    is_valid_size = is_file_size(file_content)
    
    if is_docx and is_valid_size:
        # Convert DOCX to PDF
        pdf_content = convert_docx_to_pdf(file_content)
        
        if pdf_content is not None:
            # Get the file name from the event
            file_name = event['fileName']
            
            # Remove the file extension from the file name
            file_name_without_extension = os.path.splitext(file_name)[0]
            
            # Add the .pdf extension to the file name
            pdf_file_name = file_name_without_extension + '.pdf'
            
            # Upload the PDF file to S3
            response = s3_client.put_object(
                Body=pdf_content,
                Bucket='project-fileupload',
                Key=pdf_file_name,
            )
            
            print(response)
            
            return {
                'statusCode': 200,
                'body': json.dumps('Uploaded successfully!')
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to convert DOCX to PDF!')
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid file format or size exceeded!')
        }

def is_file_docx(file_content):
    # Check the file signature to determine if it's a DOCX
    docx_signature = b'\x50\x4b\x03\x04'
    return file_content.startswith(docx_signature)

def is_file_size(file_content):
    # Check if the file size is less than 5MB
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    return len(file_content) < max_size

def convert_docx_to_pdf(file_content):
    try:
        # Create a temporary file to store the DOCX content
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            temp_docx.write(file_content)
            temp_docx_path = temp_docx.name
        
        # Create a temporary file to store the PDF content
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        # Convert the DOCX file to PDF
        convert(temp_docx_path, temp_pdf_path)
        
        # Read the converted PDF content
        with open(temp_pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        # Delete the temporary files
        os.remove(temp_docx_path)
        os.remove(temp_pdf_path)
        
        return pdf_content
    except Exception as e:
        print(f'Error converting DOCX to PDF: {str(e)}')
        return None
