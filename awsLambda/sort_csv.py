import csv

inputfile = csv.reader(open('resources.csv'))
# outputfile = open('placelist.csv','w')
subnetfile = open('subnets.csv', 'w')

for row in inputfile:
    data = {row[3]: row[0]}
    # print(data)
    for key, value in data.items():
        if key == 'Subnet':
          print(value)
          subnets = (value)
        #   print(subnets)
          subnetfile.write(subnets+'\n')
    # outputfile.write(str(data)+'\n')
    # for i in data:
    #     print(i)
