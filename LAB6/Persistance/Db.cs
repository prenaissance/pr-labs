using LAB6.Models;
using Microsoft.EntityFrameworkCore;

namespace LAB6.Persistance;

public class Db : DbContext
{
    public Db(DbContextOptions options) : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ElectroScooter>(
            entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Name).IsRequired();
                entity.Property(e => e.BatteryLevel).IsRequired();
                entity.HasData([
                    new ElectroScooter
                    {
                        Id = 1,
                        Name = "Scooter 1",
                        BatteryLevel = 90.5
                    },
                    new ElectroScooter
                    {
                        Id = 2,
                        Name = "Scooter 2",
                        BatteryLevel = 80.0
                    },
                ]);
            }
        );
    }
    public DbSet<ElectroScooter> ElectroScooters { get; set; } = default!;
}