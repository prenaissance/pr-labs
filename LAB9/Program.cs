using System.Text;
using Azure.Communication.Email;
using FluentFTP;
using LAB9.Configuration;
using LAB9.Contracts;
using Microsoft.AspNetCore.Antiforgery;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.FileProviders;

const string fromAddress = "no-reply@inventory-hub.space";
const string ftpFolder = "pneumonoultramicroscopicsilicovolcanoconiosis";
const string ftpServerUrl = "138.68.98.108";

var builder = WebApplication.CreateBuilder();

var myConfiguration = builder.Configuration.Get<MyConfiguration>()!;

// Docs: https://github.com/robinrodricks/FluentFTP/wiki/Quick-Start-Example
var ftpClient = new FtpClient(ftpServerUrl, myConfiguration.FtpUsername, myConfiguration.FtpPassword);
ftpClient.AutoConnect();
ftpClient.CreateDirectory(ftpFolder);

builder.Services
    .AddSingleton<IFtpClient>(ftpClient)
    .AddSingleton(x => new EmailClient(myConfiguration.AzureCommunicationsConnectionString));
builder.Services.AddAntiforgery();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(Path.Combine(Directory.GetCurrentDirectory(), "public")),
    RequestPath = ""
});
app.UseAntiforgery();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// app.UseHttpsRedirection();

app.MapGet("", (HttpContext httpContext, IAntiforgery antiforgery) =>
{
    string htmlTemplate = File.ReadAllText("Templates/index.html");
    var token = antiforgery.GetAndStoreTokens(httpContext);
    string hiddenInput = $"""<input name={token.FormFieldName} type="hidden" value="{token.RequestToken}" />""";
    string html = htmlTemplate.Replace("{{ csrf_field }}", hiddenInput);
    return Results.Content(html, "text/html");
});

app.MapPost("/api/send-email", async (
    [AsParameters] SendEmailRequest request,
    IFormFileCollection files,
    IFtpClient ftpClient,
    EmailClient emailClient) =>
{
    var fileUrls = new List<string>();
    // upload files to FTP server
    foreach (var file in files)
    {
        using var stream = file.OpenReadStream();
        string filePath = Path.Combine(ftpFolder, $"{DateTime.Now.ToShortTimeString()}-{file.FileName}");
        string fileUrl = $"ftp://{ftpServerUrl}/{filePath}";
        fileUrls.Add(fileUrl);
        ftpClient.UploadStream(stream, filePath);
    }
    // send email
    try
    {
        StringBuilder sb = new();
        sb.AppendLine(request.Body);
        if (files.Count > 0)
        {
            sb.AppendLine();
            sb.AppendLine("Attached files:");
            foreach (var fileUrl in fileUrls)
            {
                sb.AppendLine(fileUrl);
            }
        }
        await emailClient.SendAsync(
            Azure.WaitUntil.Completed,
            new EmailMessage(
                senderAddress: fromAddress,
                recipientAddress: request.To,
                content: new EmailContent(request.Subject)
                {
                    PlainText = sb.ToString()
                }
            )
        );

        return TypedResults.Ok();
    }
    catch (Exception e)
    {
        return Results.Problem(e.Message);
    }
});

app.Run();