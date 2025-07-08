# FedCM flow in Chromium

JS API call -> Web IDL bindings in renderer -> Create mojo connection to browser process
-> Communicate with IDP and get the token -> Return token to the render process
-> Use token to resole JS Promise

# class FederatedAuthRequestImpl

This class is the browser side implementation of the FederatedAuthRequest mojo interface.
It handles mojo connections from the render process to carry out WebID related requests.

## function OnAllConfigAndWellKnownFetched

In this function we check if the RP is authenticated for the audience and that the IDP supports bison.
If either check returns an error, the corresponding error message will be shown in the browsers console.

## function OnAccountSelected

This function sends the POST request to the IDPs assertion endpoint after the user selects an account.
Here we replace the client_id with the blinded audienceID if bison is used.

## function OnTokenResponseReceived

This function is called after we recive the token from the IDP.
Here we prepend r to the token for later checks by the RP.

# class Bison

This class implements all bison related functionality.

## function IsRPAuthenticatedForAudience

Checks if the RP is authenticated for the audience

## function getBlindedAudience

Returns the serialized blinded audienceID.

## function SerializeR

Returns the serialized r value used to blind the audienceID.