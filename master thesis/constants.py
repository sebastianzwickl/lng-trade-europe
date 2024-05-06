def get_values():
    
    # Natural Gas ... NG
    # Liquefied Natural Gas ... LNG
    
    # Energy ration between NG and LNG (same volume)
    # 1m³ LNG == 584m³ NG
    # Source : "IGU LNG Annual Report 2019"
    LNG_to_Gas = 584
    
    # 1MMBtu ... 28.263682m³ of NG 
    # Source: https://www.indexmundi.com/commodities/glossary/mmbtu
    MMBtu_LNG = LNG_to_Gas / 28.263682
    MMBtu_Gas = 1 / 28.263682
    
    # One million tons of LNG is equal to between 1.38 – 1.41 bcm of gas.
    mt_LNG_BCM = 1.379 * 10**9 # mega tonne of LNG to bcm 
    # Source: https://www.enerdynamics.com/Energy-Currents_Blog/Understanding-Liquefied-Natural-Gas-LNG-Units.aspx
    
    mt_MMBtu = mt_LNG_BCM * MMBtu_Gas
    
     #  tonne of oil to mmbtu  
    t_oil_MMBtu = 39.6526
    # Source : https://unitjuggler.com/
    
    return MMBtu_LNG, MMBtu_Gas, mt_LNG_BCM, mt_MMBtu, t_oil_MMBtu, LNG_to_Gas
    
    






           