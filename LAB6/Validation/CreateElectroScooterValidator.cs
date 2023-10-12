using FluentValidation;
using LAB6.Dtos;

namespace LAB6.Validation;

public class CreateElectroScooterValidator : AbstractValidator<CreateElectroScooterDto>
{
    public CreateElectroScooterValidator()
    {
        RuleFor(x => x.Name).NotEmpty().WithMessage("Name is required");
        RuleFor(x => x.BatteryLevel).InclusiveBetween(0, 100).WithMessage("Battery level must be between 0 and 100");
    }
}