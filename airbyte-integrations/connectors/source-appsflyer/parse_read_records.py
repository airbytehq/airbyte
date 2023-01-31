import json

filename_in = "exh.json"
filename_out = "exh_out.json"

with open(filename_in, "r") as f_in:
    with open(filename_out, "w") as f_out:
        streams_to_lines_count = {}
        line = f_in.readline()
        while line:
            try:
                line_obj = json.loads(line)
                if line_obj["type"] == "RECORD":
                    stream_name = line_obj["record"]["stream"]
                    if not streams_to_lines_count.get(stream_name):
                        streams_to_lines_count[stream_name] = 0
                    if streams_to_lines_count[stream_name] < 5:
                        f_out.write(line)
                    streams_to_lines_count[stream_name] += 1
                else:
                    f_out.write(line)
            except:
                f_out.write(line)

            line = f_in.readline()
        print(streams_to_lines_count)
