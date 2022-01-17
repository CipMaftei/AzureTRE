import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs/internal/observable/of';
import { MockTREApiService } from '../services/dre-api-core-service.mock';
import { TREApiService } from '../services/dre-api-core.service';
import { WorkspaceComponent } from './workspace.component';


let dialogSpy: jasmine.Spy;
const dialogRefSpyObj = jasmine.createSpyObj({ afterClosed: of({}), close: null });
dialogRefSpyObj.componentInstance = { body: '' };

describe('WorkspaceComponent', () => {
    let component: WorkspaceComponent;
    let fixture: ComponentFixture<WorkspaceComponent>;

    beforeEach(async () => {
        TestBed.configureTestingModule({
            imports: [
                RouterTestingModule, MatDialogModule
            ],
            declarations: [WorkspaceComponent],
            providers: [
                { provide: TREApiService, useClass: MockTREApiService }
            ],
            schemas: [
                CUSTOM_ELEMENTS_SCHEMA
            ]
        })
            .compileComponents();

        fixture = TestBed.createComponent(WorkspaceComponent);
        component = fixture.componentInstance;
        await fixture.whenStable();
        fixture.detectChanges();

        dialogSpy = spyOn(TestBed.inject(MatDialog), 'open').and.returnValue(dialogRefSpyObj);
    });

    it('should create', () => {
        expect(component).toBeDefined();
    });

    it('should render test workspaces on the page', () => {
        const pageElement: HTMLElement = fixture.nativeElement;
        const h = pageElement.querySelector('#workspaces');

        expect(h).not.toBeNull();
        expect(h.children).not.toBeNull();
        expect(h.children.length).toBe(2);
        expect(h.querySelector('#p01')).not.toBeNull();
        expect(h.querySelector('#p02')).not.toBeNull();
    });

    it('should populate workspaces array via ngOnInit', () => {
        // fixture.detectChanges() calls ngOnInit, which populates workspaces array
        expect(component.workspaces).toBeTruthy();
    });

    it('should open create workspace modal on button click', () => {
        component.openCreateWorkspaceDialog();

        expect(dialogSpy).toHaveBeenCalled();
    });
});
