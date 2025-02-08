import { NextResponse } from "next/server";

export async function GET(request, { params }) {
  const { zipCode } = await params;
  const origin_prefix = zipCode.slice(0, 3);
  const response = await fetch(
    `https://www.ups.com/media/us/currentrates/zone-csv/${origin_prefix}.xls`
  );

  if (response.ok) {
    const blob = await response.blob();
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/vnd.ms-excel",
        "Content-Disposition": `attachment; filename=${origin_prefix}.xls`,
      },
    });
  }

  return NextResponse.json({ error: "File not found" }, { status: 404 });
}
