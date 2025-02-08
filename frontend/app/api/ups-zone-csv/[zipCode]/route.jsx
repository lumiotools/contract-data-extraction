import { NextResponse } from "next/server";

export async function GET(request, { params }) {
  const { zipCode } = await params;
  const origin_prefix = zipCode.slice(0, 3);
  
  const response = await fetch(
    `https://www.ups.com/media/us/currentrates/zone-csv/${origin_prefix}.xls`
  );

  console.log("Respons from UPS Zone CSV");

  if (!response.ok) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }
  
  const reader = response.body.getReader();
  const stream = new ReadableStream({
    start(controller) {
      function push() {
        reader.read().then(({ done, value }) => {
          if (done) {
            controller.close();
            return;
          }
          controller.enqueue(value);
          push();
        });
      }
      push();
    },
  });

  return new NextResponse(stream, {
    headers: {
      "Content-Type": "application/vnd.ms-excel",
      "Content-Disposition": `attachment; filename=${origin_prefix}.xls`,
    },
  });
  //   if (response.ok) {
  //     const blob = await response.blob();
  //     return new NextResponse(blob, {
  //       headers: {
  //         "Content-Type": "application/vnd.ms-excel",
  //         "Content-Disposition": `attachment; filename=${origin_prefix}.xls`,
  //       },
  //     });
  //   }

  //   return NextResponse.json({ error: "File not found" }, { status: 404 });
}
