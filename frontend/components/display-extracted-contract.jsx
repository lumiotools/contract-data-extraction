"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

const DisplayExtractedContract = ({ details, tables }) => {
  return (
    <div className="container mx-auto p-4 [&>*]:text-white">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Carrier Information</CardTitle>
        </CardHeader>
        <CardContent>
          <p>
            <strong>Carrier:</strong> {details.carrier}
          </p>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Eligible Accounts</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Account Number</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Address</TableHead>
                <TableHead>ZIP</TableHead>
                <TableHead>Commodity Tier</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {details.eligible_accounts.map((account, index) => (
                <TableRow key={index}>
                  <TableCell>{account.account_number}</TableCell>
                  <TableCell>{account.name}</TableCell>
                  <TableCell>{account.address}</TableCell>
                  <TableCell>{account.zip}</TableCell>
                  <TableCell>{account.commodity_tier || "N/A"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Tabs defaultValue={tables[0].title.toLowerCase().replace(/\s+/g, "-")}>
        <TabsList className="w-full grid grid-cols-5">
          {tables.map((table, index) => (
            <TabsTrigger key={index} value={table.title.toLowerCase().replace(/\s+/g, "-")}>
              {table.title}
            </TabsTrigger>
          ))}
        </TabsList>

        {tables.map((table, index) => (
          <TabsContent key={index} value={table.title.toLowerCase().replace(/\s+/g, "-")}>
            <Card>
              <CardHeader>
                <CardTitle>{table.title}</CardTitle>
                <CardDescription>{table.tableData.notes?.join(" ")}</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      {table.tableData.headers.map((header, headerIndex) => (
                        <TableHead key={headerIndex}>{header}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {table.tableData.rows.map((row, rowIndex) => (
                      <TableRow key={rowIndex}>
                        {table.tableData.headers.map((header, cellIndex) => (
                          <TableCell key={cellIndex}>
                            {header === "tags" ? (
                              <div className="flex flex-wrap gap-1">
                                {row[header]?.map((tag, tagIndex) => (
                                  <Badge key={tagIndex} variant="outline">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            ) : (
                              row[header] || "N/A"
                            )}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {table.metadata && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle>Metadata</CardTitle>
                </CardHeader>
                <CardContent>
                  {table.metadata.map((meta, metaIndex) => (
                    <div key={metaIndex} className="mb-4">
                      <h4 className="font-semibold">{meta.service}</h4>
                      <ul className="list-disc pl-5">
                        {meta.notes.map((note, noteIndex) => (
                          <li key={noteIndex}>{note}</li>
                        ))}
                      </ul>
                      {meta.validityPeriod && (
                        <p className="mt-2">
                          <strong>Validity Period:</strong>{" "}
                          {meta.validityPeriod.startDate
                            ? `${meta.validityPeriod.startDate} to ${meta.validityPeriod.endDate}`
                            : "Not specified"}
                        </p>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}

export default DisplayExtractedContract

