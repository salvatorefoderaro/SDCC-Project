import minikubeservice

if __name__ == "__main__":
    address = minikubeservice.getServiceExternalIP("dashboard")
    while address == "None":
        address = minikubeservice.getServiceExternalIP("dashboardservice")
    print("L'indirizzo per accedere alla dashboard è: " + address)