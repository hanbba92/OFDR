import os,sys

a=os.path.dirname(os.path.realpath(__file__))
sys.path.append(a)

package_list=['Gage','TLS','Chamber']
for package_name in package_list:
    try:
        exec('from {s} import *'.format(s=package_name))
    except:
         print ('Skipped importing package %s.'%package_name)





