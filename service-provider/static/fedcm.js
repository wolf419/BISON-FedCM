function postAndRedirect(url, data) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = url;
    form.style.display = "none";
  
    for (const key in data) {
      const input = document.createElement("input");
      input.name = key;
      input.value = data[key];
      form.appendChild(input);
    }
  
    document.body.appendChild(form);
    form.submit();
}

function fedCMCall(mode) {
    return navigator.credentials.get({
        identity: {
            context: "signin",
            providers: [{
                configURL: "https://demo.idp/config.json",
                clientId: "https://demo.rp",
                bison: true
            }],
            mode: mode
        }
    })
}

function fedcmActiveMode(e) {
    fedCMCall("active").then(onFedCMsuccess).catch(onFedCMfailure);
}

async function onFedCMsuccess(credential) {
    let r, sig, A, B
    [r, sig, A, B] = credential.token.split(".")

    postAndRedirect("https://demo.rp:8000/login", {
        r : r,
        sig : sig,
        A : A,
        B : B
    })
}

function onFedCMfailure(e) {
    console.log(e)
}

// If the feature is available, take action
if ("IdentityCredential" in window) {
    // Add button callback for active mode
    document.getElementById('loginButton').addEventListener('click', fedcmActiveMode);

    // Add passive mode
    fedCMCall("passive").then(onFedCMsuccess).catch(onFedCMfailure);

} else {
    // FedCM is not supported, use a different identity solution
    document.getElementById("header").innerHTML = "FedCM not supported in this browser"
}