// Program used to create keypair for ransome
using System;
using System.IO;
using System.Security.Cryptography;


RSA keys = RSA.Create(2048); // Size can be changed later just will be slower to encrypt

string pubKey = keys.ExportRSAPublicKeyPem();
string privKey = keys.ExportRSAPrivateKeyPem();

string keyPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "keys");

// Write public key
using (StreamWriter pubKeyFile = new StreamWriter(Path.Combine(keyPath, "pub_key.pem")))
{
    pubKeyFile.Write(pubKey);
}

using (StreamWriter privKeyFile = new StreamWriter(Path.Combine(keyPath, "priv_key.pem")))
{
    privKeyFile.Write(privKey);
}




Console.WriteLine("Hello, World!");
