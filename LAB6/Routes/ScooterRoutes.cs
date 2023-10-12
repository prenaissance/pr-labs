using LAB6.Dtos;
using LAB6.Models;
using LAB6.Persistance;
using LAB6.Validation;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.OpenApi.Models;

namespace LAB6.Routes;

public static class ScooterRoutes
{
    public const string BASE_PATH = "/api/electro-scooters";
    public static IEndpointRouteBuilder AddElectroScooterEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup(BASE_PATH);
        group.MapPost("", CreateElectroScooter).AddEndpointFilter<ValidationFilter<CreateElectroScooterDto>>();
        group.MapGet("", GetElectroScooters);
        group.MapGet("{id}", GetElectroScooter);
        group.MapPut("{id}", UpdateElectroScooter).AddEndpointFilter<ValidationFilter<CreateElectroScooterDto>>();
        group.MapDelete("{id}", DeleteElectroScooter).WithOpenApi(
            options =>
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
            }
        );

        return app;
    }
    public static Created<ElectroScooter> CreateElectroScooter(CreateElectroScooterDto dto, Db db)
    {
        var scooter = new ElectroScooter
        {
            Name = dto.Name,
            BatteryLevel = dto.BatteryLevel
        };
        db.ElectroScooters.Add(scooter);
        db.SaveChanges();

        return TypedResults.Created($"{BASE_PATH}/{scooter.Id}", scooter);
    }

    public static Results<Ok<ElectroScooter>, NotFound> GetElectroScooter(int id, Db db)
    {
        var scooter = db.ElectroScooters.Find(id);
        if (scooter == null)
        {
            return TypedResults.NotFound();
        }
        return TypedResults.Ok(scooter);
    }

    public static Ok<List<ElectroScooter>> GetElectroScooters(Db db)
    {
        return TypedResults.Ok(db.ElectroScooters.ToList());
    }
    public static Results<Ok<ElectroScooter>, NotFound> UpdateElectroScooter(
        int id,
        CreateElectroScooterDto dto,
        Db db)
    {
        var scooter = db.ElectroScooters.Find(id);
        if (scooter == null)
        {
            return TypedResults.NotFound();
        }
        scooter.Name = dto.Name;
        scooter.BatteryLevel = dto.BatteryLevel;
        db.SaveChanges();

        return TypedResults.Ok(scooter);
    }

    [Authorize]
    public static Results<Ok<ElectroScooter>, NotFound, UnauthorizedHttpResult> DeleteElectroScooter(
        int id,
        Db db,
        HttpContext httpContext)
    {
        var scooter = db.ElectroScooters.Find(id);
        if (scooter == null)
        {
            return TypedResults.NotFound();
        }
        db.ElectroScooters.Remove(scooter);
        db.SaveChanges();

        return TypedResults.Ok(scooter);
    }
}