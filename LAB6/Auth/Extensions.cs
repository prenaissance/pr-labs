using Microsoft.OpenApi.Models;

namespace LAB6.Auth;

public static class Extensions
{
    public static RouteHandlerBuilder WithBasicSecurity(this RouteHandlerBuilder route) =>
        route.WithOpenApi(options =>
            {
                options.Security.Add(new OpenApiSecurityRequirement
                {
                    {
                        new OpenApiSecurityScheme
                        {
                            Reference = new OpenApiReference
                            {
                                Type = ReferenceType.SecurityScheme,
                                Id = "basic"
                            }
                        },
                        Array.Empty<string>()
                    }
                });
                return options;
            });
}