# DYNAMIC IMPORT PLAGIN
Sample code in a txt file that my program reads and imports: 

!PROGRAMM[OUT=0];
@New1, New2, New3, New4 = Nefile.NIL;
@KEY = 'HELLO WORLD';
@TEST = SHIFER.ENDCODE;
@APP = PRINT_SERVICE.PRINT[KEY];
 
@PHOTO = 'simpleExample.png'; 
if TkinterDisplay: {@TkinterDisplay._Call_Tkinter_;};
if ASCLII_ART: { 
    @IMAGE = ASCLII_ART.PHOTO_TO_ASCII[PHOTO]; 
    @ASCLII_ART.PHOTO_RESULT[IMAGE];
}; 

if SHIFER: {  
    @RANDOM_SHIFER = SHIFER.ENDCODE; 
    @PRINT_SERVICE.PRINT[RANDOM_SHIFER];
};
!PROGRAMM[OUT=1]; 

🟢All functions that are not in the if block are automatic.
🟢Can handle variables with ',' 
🟢Can work with if blocks  
🟢Can call functions from these plugins or just read them

⁉️Where can it be used⁉️  
1. it is used for convenient import of modules if there is no it is possible to check if it is in the code in a large code.  
2. Replacing Gui framework when it is out of place or at this stage it can be neglected.  

👁️‍🗨️Thank you for your attention👁️‍🗨️


