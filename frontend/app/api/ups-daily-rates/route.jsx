import { NextResponse } from "next/server";

export async function GET() {
  const response = await fetch(
    "https://www.ups.com/assets/resources/webcontent/en_US/daily_rates.xlsx"
  );

  if (response.ok) {
    const blob = await response.blob();
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/vnd.ms-excel",
        "Content-Disposition": "attachment; filename=daily_rates.xlsx",
      },
    });
  }

  return NextResponse.json({ error: "File not found" }, { status: 404 });
}
