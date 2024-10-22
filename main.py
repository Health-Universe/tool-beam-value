from typing import Annotated

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="BeAM Value",
    description="Calculates the difference between bedtime and AM fasting glucoses.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BeAMFormInput(BaseModel):
    """Form-based input schema for calculating the BeAM Value."""

    bedtime_glucose: float = Field(
        title="Bedtime Glucose",
        example=120.5,
        description="The glucose level before bedtime in mg/dL or mmol/L.",
        gt=0
    )
    am_fasting_glucose: float = Field(
        title="AM Fasting Glucose",
        example=90.0,
        description="The glucose level after fasting overnight in mg/dL or mmol/L.",
        gt=0
    )
    unit: str = Field(
        title="Unit",
        example="mg/dL",
        description="The unit of measurement for glucose levels. Either 'mg/dL' or 'mmol/L'.",
        pattern="^(mg/dL|mmol/L)$"
    )


class BeAMFormOutput(BaseModel):
    """Form-based output schema for BeAM value calculation results."""

    beam_value: float = Field(
        title="BeAM Value",
        example=30.5,
        description="The calculated difference between bedtime and AM fasting glucose levels.",
        format="display",
    )
    interpretation: str = Field(
        title="Interpretation",
        example="Potential dawn phenomenon; consider adjusting insulin/medication.",
        description="The interpretation of the BeAM value based on its range.",
        format="display",
    )


@app.post(
    "/calculate_beam_value/",
    response_model=BeAMFormOutput,
)
def calculate_beam_value(
   data: Annotated[BeAMFormInput, Form()],
) -> BeAMFormOutput:
    """Calculate the BeAM value and provide an interpretation based on the results.

    Args:
        data: BeAMFormInput - input data containing bedtime and AM fasting glucose levels.

    Returns:
        BeAMFormOutput: calculated BeAM value and interpretation

    """
    # Calculate BeAM Value
    conversion_factor = 18.0 if data.unit == "mmol/L" else 1.0

    # Convert glucose levels to mg/dL if needed
    bedtime_glucose_converted = data.bedtime_glucose * conversion_factor
    am_fasting_glucose_converted = data.am_fasting_glucose * conversion_factor

    # Calculate BeAM Value
    beam_value = bedtime_glucose_converted - am_fasting_glucose_converted

    # Interpret the BeAM value
    if beam_value > 20:
        interpretation = "Potential dawn phenomenon; consider adjusting insulin/medication."
    elif beam_value < -20:
        interpretation = "Potential nocturnal hypoglycemia; consider dietary adjustments."
    else:
        interpretation = "Overnight glucose levels are well-controlled."

    return BeAMFormOutput(
        beam_value=beam_value,
        interpretation=interpretation
    )

