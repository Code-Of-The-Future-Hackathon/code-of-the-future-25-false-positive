import type { Metadata } from "next";
import { Geist_Mono, Rubik_Mono_One } from "next/font/google";
import "./globals.css";
import Script from "next/script";

const geistMono = Geist_Mono({
	variable: "--font-geist-mono",
	subsets: ["latin"],
});

const rubikMonoOne = Rubik_Mono_One({
	weight: "400",
	subsets: ["latin"],
	display: "swap",
});

// const notoSansMono = Noto_Sans_Mono({
// 	weight: "400",
// 	subsets: ["latin"],
// 	display: "swap",
// });

export const metadata: Metadata = {
	title: "Create Next App",
	description: "Generated by create next app",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	const googleMapsApiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

	return (
		<html lang="en">
			<head>
				{googleMapsApiKey && (
					<>
						<Script
							src={`https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places`}
							strategy="lazyOnload"
						/>
					</>
				)}
			</head>
			<body className={`${geistMono.variable} antialiased`}>
				<div className={rubikMonoOne.className}></div>
				{children}
			</body>
		</html>
	);
}
