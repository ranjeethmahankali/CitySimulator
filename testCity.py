import citySimulator as cs
import scoring as sc

commercialComp = {'commercial':8, 'nonCommercial':1}
nonCommercialComp = {'nonCommercial':8, 'commercial':1}

commercial = cs.regionType('commercial', '#ff0000', 1, commercialComp)
nonCommercial = cs.regionType('nonCommercial', '#0000ff', -1, nonCommercialComp)

city = cs.region(600, nonCommercial, [0,0], False)

NH9 = cs.line([[0,60],[200,150],[400,450],[600,540]])
musi = cs.line([[0,350],[600,250]])

campus = cs.fence([[100,200],[200,100],[300,200],[300,400],[200,300],[100,300]])

city.tessellate(3)
city.render()

NH9.render()
musi.render()
campus.render()

cs.root.mainloop()
#print(campus.area())