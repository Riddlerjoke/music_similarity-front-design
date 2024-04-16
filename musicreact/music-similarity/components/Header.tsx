"use client";

import { useRouter } from "next/navigation"
import { twMerge } from "tailwind-merge"
import { RxCaretLeft, RxCaretRight } from "react-icons/rx"
import { HiHome } from "react-icons/hi"
import { BiSearch } from "react-icons/bi"
import { FaUserAlt } from "react-icons/fa"
import React from "react"


import Button from "./Button"
// import useAuthModal from "@/hooks/useAuthModal"
// import { useUser } from "@/hooks/useUser"
// import usePlayer from "@/hooks/usePlayer"

interface HeaderProps {
    children: React.ReactNode;
    className?: string;
}

const Header: React.FC<HeaderProps> = ({
    children,
    className
}) => {
    const router = useRouter();

    const handlelogout = () => {
        // logout();
    }
    return (
        <div className={twMerge(`
        h-fit bg-gradient-to-b from-pink-800 p-6 
        `
            , className
        )}>
            <div className={twMerge(`flex justify-between gap-x-4 items-center`)}>
                <div className={twMerge(`flex items-center gap-x-4`)}>
                    <div className={twMerge(`flex-col justify-start gap-x-4`)}>
                        <button
                            className={twMerge(`
                                border-2 justify-center bg-white rounded-full flex p-2 hover:opacity-75 transition
                                `)} >
                            <HiHome className={twMerge(`text-black`)} size={20}/>
                        </button>
                    </div>
                    <div className={twMerge(`flex-col justify-start gap-x-4`)}>
                        <button
                            className={twMerge(`
                                border-2 justify-center bg-white rounded-full flex p-2 hover:opacity-75 transition
                                `)}>
                            <BiSearch className={twMerge(`text-black`)} size={20}/>
                        </button>
                    </div>
                </div>

                <div className={twMerge(`
                    flex-col-reverse justify-end gap-x-4
                    `)}>
                    <Button
                        onClick={handlelogout}
                        className={twMerge(`
                            bg-pink-600 border-2 border-white text-white rounded-xl px-4 py-2 hover:opacity-75 transition
                            `)}>
                        Logout
                        <FaUserAlt/>
                    </Button>
                </div>

                <div className={twMerge(`flex-col justify-end gap-x-4`)}>

                    <div>
                            <Button className="bg-transparent text-neutral-300 font-medium px-4" >
                                Sign up
                            </Button>
                        </div>
                        <div>
                            <Button className="bg-white px-4 py-2" >
                                Log in
                            </Button>
                        </div>
                </div>

            </div>
            <div className={twMerge(`
            flex justify-between items-center
            `, className)}>
                <div className={twMerge(`
                flex  items-center justify-between gap-x-4
                `)}>
                    <p className={twMerge(`
                    text-white font-bold text-2xl p-4
                    `)}>
                        Music Similarity
                    </p>
                    <button
                        onClick={() => {
                            router.back();
                        }}
                        className={'rounded-full bg-black flex items-center'}>
                        <RxCaretLeft className={twMerge(`
                        text-white
                        `)} size={35}/>
                    </button>
                    <button
                        onClick={() => {
                            router.forward();
                        }}
                        className={'rounded-full bg-black flex items-center'}>
                        <RxCaretRight className={twMerge(`
                        text-white
                        `)} size={35}/>
                    </button>
                </div>
            </div>
        </div>

    )
}
export default Header;