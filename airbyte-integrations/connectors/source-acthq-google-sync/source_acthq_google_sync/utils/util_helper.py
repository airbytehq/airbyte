
from source_acthq_google_sync.utils.s3_helper import S3Helper
from source_acthq_google_sync.utils.gmail_helper import GMailHelper
import base64
import dateutil.parser as parser
import copy

class UtilHelper:

    def process_email_messages(self, email, config, logger, message_id, token, user, companyInfo):        
        self.s3 = S3Helper(config)
        try:
            inbox = GMailHelper().get_message(accessToken=token, message_id=message_id, logger=logger)
            fileName = f'{companyInfo["slug"]}/{config["customerInstanceId"]}/email-raw-response/{email}_{user["userId"]}_{inbox["id"]}_{inbox["threadId"]}_{inbox["internalDate"]}.jsonl'
            inbox['raw_s3_url'] = f'{config["s3Bucket"]}/{fileName}'
            self.s3.upload(path= config['s3Bucket'], fileName= fileName , data=inbox)
            required_mail = self.flattening(values=inbox, translated=user, companyInfo=companyInfo)
            return required_mail
        except Exception as err:
            reason = f"Failed to read data of {email}"
            logger.error(reason)
            raise err
        
    def data_encoder(self,text,typ,snippet): #Function to decode the encypted email body 
          if text and len(text)>0 :
              message = base64.urlsafe_b64decode(text.encode('UTF8'))
              message = str(message, 'utf-8')
              if typ=='text/plain':
                  return (message.split("On")[0])
              else:
                  return (snippet)
                  
          else:
              return (snippet)
    
    def message_full_recursion(self, m,snippet): #Recursive function to obtain the email body within the json response
          for i in m:       
              message=''
              mimeType = (i['mimeType'])
              if mimeType in ['text/plain']:
                  message=self.data_encoder(i['body']['data'],mimeType,snippet)
                  if message is not None:
                      return(message)
              elif 'parts' in i:
                  return(self.message_full_recursion(i['parts'],snippet))

    def flattening(self, values, translated, companyInfo):
        try:
            temp_dict=copy.deepcopy(translated)
            temp_dict.update(companyInfo)            
            temp_dict['thread_id']=values['threadId']
            temp_dict['id']=values['id']
            temp_dict['snippet']=values['snippet']
            temp_dict['historyId']=values['historyId']
            temp_dict['mail_date'] = values['internalDate']
            payload=values['payload']
            header=payload['headers']
            if 'labelIds' in values.keys():
                temp_dict['label']=values['labelIds']
            for one in header: # getting the Subject
                    if one['name'] == 'From':
                        temp_dict['msg_from'] = one['value']

                    elif one['name']=='To':
                        temp_dict['msg_to'] = one['value']
                        
                    elif one['name'] == 'Subject':
                        temp_dict['msg_subject'] = one['value']
                        
                    elif one['name']=='Cc':
                                temp_dict['mail_cc'] = one['value']
                    elif one['name']=='Bcc':
                                temp_dict['mail_bcc'] = one['value']
                    else:
                        pass
            if 'body' in payload.keys() and payload['body']['size']!=0:
                mail_body=self.data_encoder( payload['body']['data'],payload['mimeType'],values['snippet'])
            elif 'parts' in payload.keys():
                parts=payload['parts']
                mail_body=self.message_full_recursion(parts,values['snippet'])
            else:
                mail_body=values['snippet']
            temp_dict['body']=mail_body
            return temp_dict
        except Exception as e:
            print(e)        
            
    