using LAB6.Auth;
using LAB6.Dtos;
using LAB6.Models;
using LAB6.Persistance;
using LAB6.Validation;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http.HttpResults;

namespace LAB6.Routes;

public static class ScooterRoutes
{
    public const string BASE_PATH = "/api/electro-scooters";
    public static IEndpointRouteBuilder AddElectroScooterEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup(BASE_PATH);
        group.MapPost("", CreateElectroScooter)
            .AddEndpointFilter<ValidationFilter<CreateElectroScooterDto>>()
            .WithSummary("Creates a new electro scooter")
            .WithOpenApi();
        group.MapGet("", GetElectroScooters)
            .WithSummary("Returns all electro scooters")
            .WithOpenApi();
        group.MapGet("{id}", GetElectroScooter)
            .WithSummary("Returns an electro scooter by id")
            .WithOpenApi();
        group.MapPut("{id}", UpdateElectroScooter)
            .AddEndpointFilter<ValidationFilter<CreateElectroScooterDto>>()
            .WithSummary("Updates an electro scooter by id")
            .WithOpenApi();
        group.MapDelete("{id}", DeleteElectroScooter)
            .WithSummary("Deletes an electro scooter by id")
            .WithBasicSecurity();

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