while : 
do
    python do.py && (scp /media/disk/*.pdf /media/disk/*.PDF a5.creativecommons.org:/var/www/mirrors.creativecommons.org/www/ccboard/ ;
    ssh a5.creativecommons.org 'cd /var/www/mirrors.creativecommons.org/www/ccboard/ ; chmod 644 *.pdf *.PDF' ; 
    eject /media/disk ; 
    eject ; date ) || echo empty I think;
    sleep 2
done
