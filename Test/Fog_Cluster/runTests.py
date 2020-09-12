import podutility as pu
import time

if __name__ == '__main__':

    deploymentList = ['sendemail', 'dbconnector', 'collectdata', 'dashboard', 'mysql']
        
    for i in deploymentList:
        
        for j in range(1, 5):

            print("\n<<<<< Executing test for " + i + " >>>>>")
        
            pu.killPod(i, "deployment")
            time.sleep((10 * 2**j) +5)
            pu.checkPodStatus(i)
