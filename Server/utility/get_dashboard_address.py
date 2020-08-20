import minikubeservice

if __name__ == "__main__":
    address = minikubeservice.getServiceExternalIP("dashboard")
    while address == "None" or "<pending>":
        address = minikubeservice.getServiceExternalIP("dashboardservice")
    print("L'indirizzo per accedere alla dashboard è: " + address)