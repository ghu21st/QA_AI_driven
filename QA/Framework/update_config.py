import yaml
import os
file = "config/testServerConfig.yaml"

stream = open(file, 'r')
data = yaml.load(stream, Loader=yaml.FullLoader)
data['NRCAudioPath'] = os.environ.get('TESTPATH')+"/ev2/Scripts/Framework/nrctest/audio/"
with open(file, 'w') as yaml_file:
    yaml_file.write( yaml.dump(data, default_flow_style=False))