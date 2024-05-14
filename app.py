import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blog_topic: str) -> str:
    prompt = f"""<s>[INST]Human: Write a 200 words blog on the topic {blog_topic} 
    Assistant:[/INST]
    """
    
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }
    
    model_id = "meta.llama2-13b-chat-v1"
    
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1", 
                               config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId=model_id)
        
        # Decode the native response body.
        model_response = json.loads(response["body"].read())

        # Extract and print the generated text.
        blog_details = model_response["generation"]
        
        return blog_details
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""
    
def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client("s3")
    
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Code Saved to S3")
    except Exception as e:
        print(f"Error saving code to s3: {e}")

def lambda_handler(event, context):
    event = json.loads(event["body"])
    blog_topic = event["blog_topic"]
    
    generate_blog = blog_generate_using_bedrock(blog_topic=blog_topic)
    
    if generate_blog:
        current_time = datetime.now().strftime("%H%M%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = "aws_bedrock_course1"
        save_blog_details_s3(s3_key, s3_bucket, generate_blog)
    else:
        print("No blog was generated.")
    
    return {
        "status_code": 200,
        "body": json.dumps('Blog generated successfully')
    }