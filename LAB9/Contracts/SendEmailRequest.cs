using Microsoft.AspNetCore.Mvc;

namespace LAB9.Contracts;

public class SendEmailRequest
{
    [FromForm] public required string To { get; set; }
    [FromForm] public required string Subject { get; set; }
    [FromForm] public required string Body { get; set; }
}