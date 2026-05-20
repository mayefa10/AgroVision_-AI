const AI_API = "http://localhost:8000";

export async function getClimateData(
  department: string,
  days: number = 30
) {
  const response = await fetch(
    `${AI_API}/clima/nasa/${department}?days=${days}`
  );

  if (!response.ok) {
    throw new Error("Error fetching climate data");
  }

  return response.json();
}