import argparse
import datetime
import json
import os 


import sys
from pprint import pprint
import requests

def read_json(filepath):
    with open(filepath,"r") as f:
        return json.loads(f.read())


def log(message):
    log_json={"type":"LOG","log":message}
    print(json.dumps(log_json))



def spec():
    #reading json contents
    current_script_dir=os.path.dirname(os.path.realpath(__file__))
    spec_path=os.path.join(current_script_dir,"spec.json")
    specification=read_json(spec_path)

    airbyte_msg={"type":"SPEC","spec":specification}
    print(json.dumps(airbyte_msg))



def check(config):

    response=requests.get("https://cloud.iexapis.com/v1/"+"stock/"+config["stock_ticker"]+"/previous"+"?token="+config["api_key"])
    if response.status_code==200:
        result={"status":"SUCCEEDED"}
    elif response.status_code==403:
        result={"status":"FAILED","message":"API Key is incorrect"}
    else:
        result={"status": "FAILED", "message": "Input configuration is incorrect. Please verify the input stock ticker and API key."}

    output_message={"type":"CONNECTION_STATUS","connectionStatus":result}

    print(json.dumps(output_message))

#to check if file is in absolute path..else it reads from the cwd...used in command check to know the file path of config file
def input_file_path(path):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(os.getcwd(),path)


def discover(config):
    catalog={   
                "streams":[{
                        "name":"stock_prices",
                        "supported_sync_modes":["full_refresh"],
                        "json_schema":{
                            "properties":{
                                "date":{"type":"string"},
                                "price":{"type":"number"},
                                "stock_ticker":{"type":"string"}

                                }
                            }
                        }
                    ]
                }
    airbyte_msg={"type":"CATALOG","catalog":catalog}
    print(json.dumps(airbyte_msg))

def read(config,catalog):
    stock_prices_stream=None
    for configured_stream in catalog["streams"]:
        if configured_stream["stream"]["name"]=="stock_prices":
            stock_prices_stream=configured_stream

        if stock_prices_stream==None:
            log("No stream selected")
        
        if stock_prices_stream["sync_mode"]!='full_refresh':
            log("it supports only full refresh")
            sys.exit(1)

        api_key=config['api_key']
        stock_ticker=config['stock_ticker']
        
        response=requests.get("https://cloud.iexapis.com/v1"+"/stock/"+stock_ticker+"/chart/7d?token="+api_key)

        #https://cloud.iexapis.com/v1/stock/TSLA/chart/7d?token=pk_88ebf6552c274e50bf20a45c49e8d7b3

        if response.status_code!=200:
            log("failure occured when call iex api")
            sys.exit(1)
        
        else:
            prices=sorted(response.json(),key=lambda record:datetime.datetime.strptime(record["date"],'%Y-%m-%d') )
            for price in prices:
                data={"date":price["date"],"stock_ticker":price["symbol"],"price":price["close"]}
                #print(json.dumps(data))
                record={"stream":"stock_prices","data":data,"emitted_at":int(datetime.datetime.now().timestamp())*1000}
                output_msg={"type":"RECORD","record":record}

                print(json.dumps(output_msg))




def run(args):
    parent_parser = argparse.ArgumentParser(add_help=False)
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(title="commands", dest="command")
    
    #Accept the spec command
    subparsers.add_parser("spec", help="outputs the json configuration specification", parents=[parent_parser])

    #Accept the check command
    check_parser=subparsers.add_parser("check",help="checks the config used to connect",parents=[parent_parser]) 
    required_check_parser=check_parser.add_argument_group("required named arguments")
    required_check_parser.add_argument("--config",type=str,required=True,help="path to json config file")
    
    #Accept the discover command
    discover_parser=subparsers.add_parser("discover",help="outputs a catalog desc",parents=[parent_parser])
    required_discover_parser=discover_parser.add_argument_group("req named args")
    required_discover_parser.add_argument("--config",type=str, required=True, help="path to the json configuration file")

    #Accept the read command
    read_parser=subparsers.add_parser("read",help="read input from source and o/p's msg to stdout",parents=[parent_parser])  
    #state is optional argument
    read_parser.add_argument("--state", type=str, required=False, help="path to the json-encoded state file")

    required_read_parser = read_parser.add_argument_group("required named arguments")
    required_read_parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
    required_read_parser.add_argument("--catalog", type=str, required=True, help="path to the catalog used to determine which data to read")


    parsed_args = main_parser.parse_args(args)
    command = parsed_args.command

    if command == "spec":
        spec()

    elif command=="check":
        # get the config file path
        config_file_path=input_file_path(parsed_args.config)
        config=read_json(config_file_path)
        check(config)

    elif command=="discover":
        config_file_path=input_file_path(parsed_args.config)
        config=read_json(config_file_path)
        discover(config)
    elif command=="read":
        config=read_json(input_file_path(parsed_args.config))
        config_catalog=read_json(input_file_path(parsed_args.catalog))        
        read(config,config_catalog)
   

    else:
    # If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
        # had a failure
        log("Invalid command. Allowable commands: [spec,check,read,discover]")
        sys.exit(1)

    # A zero exit code means the process successfully completed    
    sys.exit(0)

def main():
    arguments = sys.argv[1:]
    run(arguments)


if __name__ == "__main__":
    main()
