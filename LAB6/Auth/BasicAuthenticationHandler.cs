using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text;
using System.Text.Encodings.Web;
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Options;

namespace LAB6.Auth;

public class BasicAuthenticationHandler(
    IOptionsMonitor<AuthenticationSchemeOptions> options,
    ILoggerFactory logger,
    UrlEncoder encoder) : AuthenticationHandler<AuthenticationSchemeOptions>(options, logger, encoder)
{
    private const string PASSWORD = "1";

    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.ContainsKey("Authorization"))
        {
            return Task.FromResult(AuthenticateResult.Fail("Missing Authorization Header"));
        }

        var authHeader = AuthenticationHeaderValue.Parse(Request.Headers["Authorization"]!);
        var credentialBytes = Convert.FromBase64String(authHeader.Parameter!);
        if (Encoding.UTF8.GetString(credentialBytes).Split(":") is not [string username, string password])
        {
            return Task.FromResult(AuthenticateResult.Fail("Invalid Authorization Header"));
        }

        if (password != PASSWORD)
        {
            return Task.FromResult(AuthenticateResult.Fail("Invalid Password"));
        }

        var claims = new[] { new Claim(ClaimTypes.Name, username) };
        var identity = new ClaimsIdentity(claims, Scheme.Name);
        var principal = new ClaimsPrincipal(identity);
        var ticket = new AuthenticationTicket(principal, Scheme.Name);

        return Task.FromResult(AuthenticateResult.Success(ticket));
    }
}